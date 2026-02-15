# Humidity and Temperature sensor 


![Grafana screenshot](/docs/grafana.png)

pip install prometheus-client

sudo nano /etc/systemd/system/

```
sudo mkdir -p /opt/prometheus
sudo nano /opt/prometheus/prometheus.yml
```

```
sudo mkdir -p /opt/prometheus/data
sudo chown -R 65534:65534 /opt/prometheus
```



docker run -d \
  --name prometheus \
  --net=host \
  -v /opt/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro \
  -v /opt/prometheus/data:/prometheus \
  prom/prometheus


nohup python humidity_exporter.py &