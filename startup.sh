while ! sudo add-apt-repository -y ppa:ettusresearch/uhd
do
    echo Failed to get ettusreasearch ppa, retrying
done
while ! sudo add-apt-repository -y ppa:johnsond-u/sdr
do
    echo Failed to get johnsond ppa, retrying
done
while ! sudo apt-get update
do
    echo Failed to update, retrying
done

for thing in $*
do
    case $thing in
        gnuradio)
            while ! sudo DEBIAN_FRONTEND=noninteractive apt-get install -y gnuradio
            do
                echo Failed to get gnuradio, retrying
            done
            ;;

        srslte)
            while ! sudo DEBIAN_FRONTEND=noninteractive apt-get install -y srslte
            do
                echo Failed to get srsLTE, retrying
            done
            ;;
    esac
done

while ! sudo "/usr/lib/uhd/utils/uhd_images_downloader.py"
do
    echo Failed to download uhd images, retrying
done
