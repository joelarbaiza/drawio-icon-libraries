<#
.SYNOPSIS
    Instala o actualiza las librerías de drawio-icon-libraries en Draw.io de escritorio (Windows).

.DESCRIPTION
    Deja en una carpeta fija las librerías de la última release y las mantiene al día.

    - Actualizar: si Draw.io ya tiene cargadas las librerías desde una carpeta (importadas antes),
      el script reemplaza los archivos de esa carpeta. Al abrir Draw.io se ven los iconos nuevos,
      sin duplicados y sin pasos manuales.
    - Primera vez: copia las librerías a %LOCALAPPDATA%\drawio-icon-libraries\libraries, abre esa
      carpeta y Draw.io, y explica el único paso manual: importar cada .xml una vez con
      Archivo > Abrir biblioteca desde > Archivo... Draw.io las recuerda; desde entonces, volver a
      ejecutar este instalador las actualiza solo.

    Por qué la primera vez es manual (comprobado en el código de Draw.io de escritorio 31.x):
    solo lee archivos locales que el usuario abrió con su diálogo, no puede cargar librerías desde
    URLs y su parámetro de arranque «clibs» admite una sola librería. Ver docs/ARCHITECTURE.md.

    El script solo LEE el estado de Draw.io (%APPDATA%\draw.io) para detectar dónde están ya cargadas
    las librerías; nunca lo modifica. Recuerda la carpeta usada en
    %LOCALAPPDATA%\drawio-icon-libraries\install-dir.txt para las siguientes actualizaciones.

.PARAMETER InstallDir
    Carpeta donde se instalan las librerías (la que contiene Azure\, Fabric\, ...). Por defecto: la
    usada la última vez, la carpeta desde la que Draw.io ya las tiene cargadas, o
    %LOCALAPPDATA%\drawio-icon-libraries\libraries.

.PARAMETER Source
    ZIP o carpeta local con las librerías en lugar de descargar la última release.

.PARAMETER Library
    Instala solo estas librerías (por nombre, p. ej. "Azure Web","Microsoft Fabric"). Por defecto, todas.

.PARAMETER NoLaunch
    No abre Draw.io ni el Explorador al terminar.

.EXAMPLE
    # Doble clic en install-drawio-desktop.bat (dentro del ZIP de la release).

.EXAMPLE
    # Desde cualquier PowerShell, sin descargar nada antes:
    irm https://raw.githubusercontent.com/joelarbaiza/drawio-icon-libraries/main/scripts/install-drawio-desktop.ps1 | iex

.EXAMPLE
    # Con parámetros:
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/joelarbaiza/drawio-icon-libraries/main/scripts/install-drawio-desktop.ps1))) -Library "Azure Web","Microsoft Fabric"
#>
[CmdletBinding()]
param(
    [string]$InstallDir,
    [string]$Source,
    [string[]]$Library,
    [switch]$NoLaunch
)

$ErrorActionPreference = 'Stop'
$ZipUrl = 'https://github.com/joelarbaiza/drawio-icon-libraries/releases/latest/download/drawio-icon-libraries.zip'
$AppDir = Join-Path $env:LOCALAPPDATA 'drawio-icon-libraries'
$DefaultInstallDir = Join-Path $AppDir 'libraries'
$MarkerFile = Join-Path $AppDir 'install-dir.txt'

function Write-Step([string]$Text) { Write-Host "`n==> $Text" -ForegroundColor Cyan }
function Write-Ok([string]$Text) { Write-Host "    $Text" -ForegroundColor Green }
function Write-Note([string]$Text) { Write-Host "    $Text" }
function Write-Warn([string]$Text) { Write-Host "    $Text" -ForegroundColor Yellow }

# --------------------------------------------------------------- Draw.io --

function Find-DrawIo {
    $candidates = @(
        (Join-Path $env:ProgramFiles 'draw.io\draw.io.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\draw.io\draw.io.exe')
    )
    if (${env:ProgramFiles(x86)}) { $candidates += (Join-Path ${env:ProgramFiles(x86)} 'draw.io\draw.io.exe') }
    $appPath = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\draw.io.exe' -ErrorAction SilentlyContinue
    if ($appPath -and $appPath.'(default)') { $candidates += $appPath.'(default)' }
    foreach ($c in $candidates) { if ($c -and (Test-Path $c)) { return $c } }
    return $null
}

function Wait-DrawIoClosed {
    while (Get-Process -Name 'draw.io' -ErrorAction SilentlyContinue) {
        # Sin consola interactiva no se puede esperar al usuario: evita un bucle infinito.
        if ([Console]::IsInputRedirected) { throw 'Draw.io está abierto. Ciérralo y vuelve a ejecutar el instalador.' }
        Write-Warn 'Draw.io está abierto. Ciérralo (guarda tus diagramas) y pulsa Enter para continuar...'
        [void](Read-Host)
    }
}

# Devuelve el contenido de un archivo de LevelDB como texto. Los .log se escriben en bloques de 32 KB
# con una cabecera de 7 bytes por fragmento (crc 4, longitud 2, tipo 1); un registro largo queda partido
# entre bloques, así que se recompone antes de buscar en él. Las tablas .ldb suelen ir comprimidas
# (Snappy) y no se interpretan: se leen tal cual por si acaso.
function Read-LevelDbText([string]$Path) {
    # Lectura compartida: no falla aunque Draw.io tenga el archivo abierto.
    $stream = New-Object IO.FileStream($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
    try {
        $bytes = New-Object byte[] $stream.Length
        $read = 0
        while ($read -lt $bytes.Length) {
            $n = $stream.Read($bytes, $read, $bytes.Length - $read)
            if ($n -le 0) { break }
            $read += $n
        }
    } finally { $stream.Dispose() }
    if (-not $Path.EndsWith('.log')) { return [Text.Encoding]::UTF8.GetString($bytes) }

    $blockSize = 32768
    $out = New-Object IO.MemoryStream
    $record = New-Object IO.MemoryStream
    $pos = 0
    while ($pos -lt $bytes.Length) {
        $blockEnd = [Math]::Min($pos - ($pos % $blockSize) + $blockSize, $bytes.Length)
        if ($blockEnd - $pos -lt 7) { $pos = $blockEnd; continue }
        $length = $bytes[$pos + 4] + 256 * $bytes[$pos + 5]
        $type = $bytes[$pos + 6]
        if ($type -eq 0 -or $pos + 7 + $length -gt $blockEnd) { $pos = $blockEnd; continue }
        $data = $pos + 7
        switch ($type) {
            1 { $out.Write($bytes, $data, $length); $out.WriteByte(10) }                 # FULL
            2 { $record.SetLength(0); $record.Write($bytes, $data, $length) }            # FIRST
            3 { $record.Write($bytes, $data, $length) }                                   # MIDDLE
            4 { $record.Write($bytes, $data, $length); $record.WriteTo($out); $out.WriteByte(10) }  # LAST
        }
        $pos = $data + $length
    }
    return [Text.Encoding]::UTF8.GetString($out.ToArray())
}

# Librerías de escritorio que Draw.io tiene cargadas (lectura de mejor esfuerzo de su localStorage).
# Devuelve las rutas locales completas; vacío si no se puede leer.
function Get-LoadedLibraryPaths {
    $dir = Join-Path $env:APPDATA 'draw.io\Local Storage\leveldb'
    if (-not (Test-Path $dir)) { return @() }

    # Tablas .ldb por antigüedad y el registro .log (lo más reciente) al final; gana la última aparición.
    $files = @(Get-ChildItem $dir -Filter '*.ldb' | Sort-Object Name) + @(Get-ChildItem $dir -Filter '*.log' | Sort-Object Name)
    $ids = @()
    foreach ($f in $files) {
        try { $text = Read-LevelDbText $f.FullName } catch { continue }
        $found = [regex]::Matches($text, '"customLibraries":\[([^\]]*)\]')
        if ($found.Count -gt 0) {
            $last = $found[$found.Count - 1].Groups[1].Value
            $ids = @([regex]::Matches($last, '"([^"]+)"') | ForEach-Object { $_.Groups[1].Value })
        }
    }
    # Se comparan rutas y no ids: .NET y JavaScript codifican distinto algunos caracteres ( ) ! * '.
    @($ids | Where-Object { $_.StartsWith('S') } | ForEach-Object {
        try { [IO.Path]::GetFullPath([uri]::UnescapeDataString($_.Substring(1))) } catch { }
    })
}

# Carpeta desde la que Draw.io ya tiene cargadas nuestras librerías (si las importaste antes).
function Find-ExistingInstall([string[]]$LoadedPaths, [string[]]$RelativePaths) {
    $roots = @{}
    foreach ($path in $LoadedPaths) {
        foreach ($rel in $RelativePaths) {
            $suffix = '\' + $rel.Replace('/', '\')
            if ($path.EndsWith($suffix, [StringComparison]::OrdinalIgnoreCase)) {
                $root = $path.Substring(0, $path.Length - $suffix.Length)
                $roots[$root] = 1 + [int]$roots[$root]
            }
        }
    }
    if ($roots.Count -eq 0) { return $null }
    return ($roots.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key
}

# ------------------------------------------------------------- Librerías --

function Get-LibrariesFolder([string]$SourcePath) {
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ('drawio-icon-libraries-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tmp | Out-Null

    if (-not $SourcePath) {
        $zip = Join-Path $tmp 'drawio-icon-libraries.zip'
        Write-Note "Descargando $ZipUrl"
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $ZipUrl -OutFile $zip -UseBasicParsing
        $SourcePath = $zip
    }

    if ((Test-Path $SourcePath -PathType Leaf) -and $SourcePath.ToLower().EndsWith('.zip')) {
        Expand-Archive -Path $SourcePath -DestinationPath $tmp -Force
        $SourcePath = $tmp
    }

    # Admite la raíz del ZIP (drawio-icon-libraries\libraries), una carpeta con libraries\ o la propia carpeta.
    foreach ($c in @((Join-Path $SourcePath 'drawio-icon-libraries\libraries'), (Join-Path $SourcePath 'libraries'), $SourcePath)) {
        if ((Test-Path $c -PathType Container) -and (Get-ChildItem $c -Recurse -Filter '*.xml' | Select-Object -First 1)) {
            return @{ Libraries = (Resolve-Path $c).Path; Temp = $tmp }
        }
    }
    throw "No se encontraron librerías .xml en $SourcePath"
}

# ------------------------------------------------------------------ Main --

function Invoke-Install {
    if ($env:OS -ne 'Windows_NT') { throw 'Este instalador es solo para Windows. En macOS/Linux importa los .xml a mano (File > Open Library from > File).' }

    Write-Host 'drawio-icon-libraries · instalación en Draw.io de escritorio' -ForegroundColor White

    $drawio = Find-DrawIo
    if (-not $drawio) {
        throw 'No se encontró Draw.io de escritorio. Instálalo desde https://github.com/jgraph/drawio-desktop/releases o usa los enlaces «Open ↗» del README en la versión web.'
    }
    Write-Note "Draw.io: $drawio"
    Wait-DrawIoClosed

    Write-Step 'Obteniendo las librerías'
    # Ejecutado como archivo junto a la carpeta libraries\ del ZIP: usa esas librerías, sin descargar.
    if (-not $Source -and $PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot 'libraries'))) {
        $Source = $PSScriptRoot
    }
    if ($Source) { Write-Note "Origen: $Source" }
    $src = Get-LibrariesFolder $Source
    try {
        $all = @(Get-ChildItem $src.Libraries -Recurse -Filter '*.xml' | ForEach-Object {
            [pscustomobject]@{
                Name     = $_.BaseName
                Relative = $_.FullName.Substring($src.Libraries.Length + 1).Replace('\', '/')
                File     = $_.FullName
            }
        })
        if ($Library) {
            $wanted = $Library | ForEach-Object { $_.ToLower() }
            $selected = @($all | Where-Object { $wanted -contains $_.Name.ToLower() })
            $missing = @($Library | Where-Object { $all.Name -notcontains $_ })
            if ($missing.Count -gt 0) { throw "Librería(s) no encontrada(s): $($missing -join ', '). Disponibles: $(($all.Name | Sort-Object) -join ', ')" }
        } else {
            $selected = $all
        }
        Write-Ok "$($selected.Count) librería(s)"

        Write-Step 'Buscando la instalación (solo lectura)'
        $loaded = @(Get-LoadedLibraryPaths)
        $previous = $null
        if (Test-Path $MarkerFile) {
            $previous = (Get-Content $MarkerFile -Raw -Encoding UTF8).Trim()
            if (-not (Test-Path $previous)) { $previous = $null }
        }
        if ($InstallDir) {
            Write-Note "Carpeta indicada con -InstallDir: $InstallDir"
        } elseif ($previous) {
            $InstallDir = $previous
            Write-Ok "Instalación anterior: $InstallDir"
        } else {
            $existing = Find-ExistingInstall $loaded ($all | ForEach-Object Relative)
            if ($existing) {
                $InstallDir = $existing
                Write-Ok "Draw.io ya usa estas librerías desde: $InstallDir"
            } else {
                $InstallDir = $DefaultInstallDir
                Write-Note "Primera instalación: $InstallDir"
                if ($loaded.Count -eq 0) {
                    Write-Warn 'Si ya importaste estas librerías desde otra carpeta, vuelve a ejecutar con'
                    Write-Warn '-InstallDir "<esa carpeta>" para actualizarlas allí y evitar duplicados.'
                }
            }
        }
        $InstallDir = [IO.Path]::GetFullPath($InstallDir)

        Write-Step "Copiando a $InstallDir"
        foreach ($lib in $selected) {
            $dest = Join-Path $InstallDir $lib.Relative.Replace('/', '\')
            New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null
            Copy-Item $lib.File $dest -Force
            $lib | Add-Member -NotePropertyName Installed -NotePropertyValue $dest -Force
        }
        $sources = Join-Path (Split-Path $src.Libraries) 'SOURCES.md'
        if (Test-Path $sources) { Copy-Item $sources (Join-Path $InstallDir 'SOURCES.md') -Force }
        New-Item -ItemType Directory -Path $AppDir -Force | Out-Null
        [IO.File]::WriteAllText($MarkerFile, $InstallDir, (New-Object Text.UTF8Encoding $false))
        Write-Ok "$($selected.Count) archivo(s) actualizados"
    }
    finally {
        Remove-Item $src.Temp -Recurse -Force -ErrorAction SilentlyContinue
    }

    # -notcontains no distingue mayúsculas: compara rutas de Windows correctamente.
    $pending = @($selected | Where-Object { $loaded -notcontains $_.Installed })

    Write-Step 'Listo'
    if ($pending.Count -eq 0) {
        Write-Ok 'Draw.io ya tenía estas librerías cargadas: al abrirlo verás los iconos actualizados.'
        if (-not $NoLaunch) { Start-Process -FilePath $drawio }
        return
    }

    if ($previous -and $loaded.Count -eq 0) {
        # La lista de Draw.io no se pudo leer (base compactada): no se sabe qué falta, solo se orienta.
        Write-Ok "Librerías actualizadas en $InstallDir."
        Write-Note 'Las que ya tenías importadas desde esta carpeta se verán actualizadas al abrir Draw.io.'
        Write-Note 'Si falta alguna: Archivo > Abrir biblioteca desde > Archivo... y elige su .xml en esa carpeta.'
        if (-not $NoLaunch) { Start-Process -FilePath $drawio }
        return
    }
    if ($pending.Count -lt $selected.Count) {
        Write-Ok "$($selected.Count - $pending.Count) librería(s) ya estaban cargadas y quedan actualizadas."
    }
    Write-Host ''
    Write-Warn "Importa una sola vez cada librería nueva ($($pending.Count)) en Draw.io:"
    Write-Note '  Archivo > Abrir biblioteca desde > Archivo...   (en inglés: File > Open Library from > File...)'
    Write-Note "  y elige el .xml en la carpeta que se va a abrir: $InstallDir"
    Write-Note '  Draw.io las recuerda. Para actualizarlas en el futuro, vuelve a ejecutar este instalador.'
    foreach ($lib in $pending | Select-Object -First 10) { Write-Note "    - $($lib.Relative)" }
    if ($pending.Count -gt 10) { Write-Note "    ... y $($pending.Count - 10) más" }

    if (-not $NoLaunch) {
        Start-Process -FilePath 'explorer.exe' -ArgumentList "`"$InstallDir`""
        Start-Process -FilePath $drawio
    }
}

# Errores con un mensaje claro y sin volcado técnico. Sin «exit»: con «irm … | iex» cerraría la
# ventana de PowerShell del usuario.
try {
    Invoke-Install
}
catch {
    Write-Host ''
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $global:LASTEXITCODE = 1
}
