foreach($line in Get-Content .\.env)
{
	$content = $line.Split("=")
	$key = $content[0]
	$value = $content[1..($content.Length - 1)] -join '='
	
	#echo "Key = ${key}, Value = ${value}"
	
	Set-Item -Path Env:${key}  -Value $value
}