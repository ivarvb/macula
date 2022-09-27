#!/bin/bash
EV="./python/python38macula/"
APP="./sourcecode/src/vx/macula/"
SRC="./sourcecode/src/"
install () {
    #sudo apt-get install python3-venv
    #sudo apt install python3-pip
    #sudo apt-get install libsuitesparse-dev
    #sudo apt install libx11-dev
    #############sudo apt install nvidia-cuda-toolkit
    rm -r $EV
    mkdir $EV
    python3 -m venv $EV
    source $EV"bin/activate"
    pip3 install -r $APP"/zrequeriments.txt"
}

convert () {
    source $EV"bin/activate"
    cd $APP
    python3 Macula.py
}
convert2 () {
    source $EV"bin/activate"
    cd $APP
    python3 Ma2.py
}
convert2_2 () {
    source $EV"bin/activate"
    cd $APP
    python3 Ma2_2.py
}
measure () {
    source $EV"bin/activate"
    cd $APP
    python3 Measure.py
}
execute () {
    source $EV"bin/activate"

    cd $SRC
    python3 Macula.py
    #cd $APP
    #python3 Server.py
}



args=("$@")
T1=${args[0]}
FILEINPUT=${args[1]}
if [ "$T1" = "install" ]; then
    install
elif [ "$T1" = "convert" ]; then
    convert
elif [ "$T1" = "convert2" ]; then
    convert2
elif [ "$T1" = "measure" ]; then
    measure

elif [ "$T1" = "convert22" ]; then
    convert2_2
else
    execute
fi
