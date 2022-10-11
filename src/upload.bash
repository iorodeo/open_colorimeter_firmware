for entry in *
do
    case $entry in 
        code.py)
            echo $entry "->" /media/$USER/CIRCUITPY
            cp $entry /media/$USER/CIRCUITPY
            ;;
        *.py)
            echo $entry "->" /media/$USER/CIRCUITPY/src
            mkdir -p /media/$USER/CIRCUITPY/src
            cp $entry /media/$USER/CIRCUITPY/src
            ;;
    esac
done
sync
