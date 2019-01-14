apt-get update -y
apt-get install wget apt-transport-https -y

wget -q https://packages.microsoft.com/config/ubuntu/16.04/packages-microsoft-prod.deb
dpkg -i packages-microsoft-prod.deb

apt-get update
apt-get install aspnetcore-runtime-2.1 -y

pip install grpcio opencensus

mkdir /lf

apt-get update && apt-get install -y --no-install-recommends ca-certificates curl
rm -rf /var/lib/apt/lists/*

curl -L --retry 5 --retry-delay 0  --retry-max-time 40  'https://github.com/Microsoft/ApplicationInsights-LocalForwarder/releases/download/v0.1-beta1/LF-ConsoleHost-linux-x64.tar.gz' -o /lf/LF-ConsoleHost-linux-x64.tar.gz

tar -xvzf /lf/LF-ConsoleHost-linux-x64.tar.gz -C /lf/

chmod +x /lf/Microsoft.LocalForwarder.ConsoleHost