echo Building executables...
pyinstaller -i ./icons/icon1.ico  -w demo1.py
pyinstaller -i ./icons/icon2.ico  -w demo2.py
pyinstaller -i ./icons/icon3.ico  -w demo3.py
echo Copying files...
mkdir ".\finals\"
copy ".\dist\demo1\demo1.exe" ".\finals\Old Method (Demo 1).exe"
copy ".\dist\demo2\demo2.exe" ".\finals\Playground (Demo 2).exe"
copy ".\dist\demo3\demo3.exe" ".\finals\Read-time Rendering (Demo 3).exe"
mkdir ".\finals\_internal\"
xcopy /e ".\dist\demo2\_internal\" ".\finals\"
mkdir ".\finals\icons\"
xcopy /e ".\icons\" ".\finals\"
mkdir ".\finals\test_imgs\"
xcopy /e ".\test_imgs\" ".\finals\"
copy ".\README.md" ".\finals"
copy ".\liquidglass.py" ".\finals"
echo Cleaning up...
rmdir /s .\dist\
rmdir /s .\build\
echo ====================
echo Build completed
pause