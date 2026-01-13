cd ..
RD /S /Q "target"
robocopy . target/python /MIR /XD .git target
cd target/python
pip freeze > requirements.txt
pip install --target . -r resource/requirements.txt
xcopy "libs\" "." /E /I /Y
cd ..
REM zip -r python.zip target
powershell -Command "Compress-Archive -Path 'python' -DestinationPath 'python.zip' -Force"
RD /S /Q "python"