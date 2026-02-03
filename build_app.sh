echo Building executables...
pyinstaller -i ./icons/icon1.ico --noconfirm --log-level=ERROR -w demo1.py
echo Demo 1 built
pyinstaller -i ./icons/icon2.ico --noconfirm --log-level=ERROR -w demo2.py
echo Demo 2 built
pyinstaller -i ./icons/icon3.ico --noconfirm --log-level=ERROR -w demo3.py
echo Demo 3 built
echo Copying files...
mkdir "./finals/"
cp -r "./dist/demo1.app" "./finals/Old Method (Demo 1).app"
cp -r "./dist/demo2.app" "./finals/Playground (Demo 2).app"
cp -r "./dist/demo3.app" "./finals/Real-time Rendering (Demo 3).app"
echo Demo apps copyed
mkdir "./finals/icons/"
cp -r "./icons/" "./finals/icons/"
mkdir "./finals/test_imgs/"
cp -r "./test_imgs/" "./finals/test_imgs/"
echo Icons and images copyed
cp "./README.md" "./finals"
cp "./liquidglass.py" "./finals"
echo Instruction and core copyed
echo Cleaning up...
rm -rf ./dist/
rm -rf ./build/
echo "===================="
echo Build completed