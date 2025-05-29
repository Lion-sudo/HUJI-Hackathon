# Start the FastAPI server
Start-Process -NoNewWindow -WorkingDirectory "./server" -FilePath "uvicorn" -ArgumentList "main:app --reload"
Start-Sleep -Seconds 2
# Start the React client
Start-Process -NoNewWindow -WorkingDirectory "./client" -FilePath "npm" -ArgumentList "start"
Write-Host "Both server and client have been started." 