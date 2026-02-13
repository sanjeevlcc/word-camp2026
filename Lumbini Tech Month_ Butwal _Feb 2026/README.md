 
************************************
Traditional → Docker → Kubernetes
************************************







************************************
1)  Create the project
************************************



Step 1.1 — Create folder structure
-------------------------------------------
mkdir -p ~/university-portal/templates
cd ~/university-portal





Step 1.2 — Create requirements.txt
-------------------------------------------
cat > requirements.txt <<'EOF'
flask==3.0.3
gunicorn==22.0.0
werkzeug==3.0.3
EOF






Step 1.3 — Create app.py
-------------------------------------------
https://github.com/sanjeevlcc/word-camp2026/blob/main/Lumbini%20Tech%20Month_%20Butwal%20_Feb%202026/app.py




Step 1.4 — Create templates/index.html (single UI file)
-------------------------------------------
https://github.com/sanjeevlcc/word-camp2026/blob/main/Lumbini%20Tech%20Month_%20Butwal%20_Feb%202026/templates/index.html














******************************************
2) Traditional Ubuntu (show: crash = DOWN)
******************************************


Step 2.1 — Install Python tools
-------------------------------------------
sudo apt update
sudo apt install -y python3 python3-venv python3-pip



Step 2.2 — Create venv + install dependencies
-------------------------------------------
pwd
cd ~/university-portal
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt



Step 2.3 — Run with Gunicorn (1 worker = full downtime demo
-------------------------------------------
export APP_SECRET="change-me"
export RUN_MODE="Traditional (Ubuntu)"
gunicorn -w 1 -b 0.0.0.0:5000 app:app



Step 2.4 — Open in browser
-------------------------------------------
http://SERVER_IP:5000

      Login:
          admin / Admin@123


Step 2.5 — Crash the whole app 
          (proves traditional downtime)
-------------------------------------------

      Open:    http://SERVER_IP:5000/crash


    Now refresh home:  http://SERVER_IP:5000

✅ It should be DOWN until you manually restart Gunicorn.









******************************************
3) Docker (packaging + faster restart) 
******************************************

Step 3.1 — Install Docker (if needed)
-------------------------------------------
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker

docker --version




Step 3.2 — Create Dockerfile
-------------------------------------------

cd ~/university-portal

cat > Dockerfile <<'EOF'
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates ./templates

ENV RUN_MODE="Docker"
ENV APP_SECRET="change-me"

EXPOSE 5000
CMD ["gunicorn","-w","1","-b","0.0.0.0:5000","app:app"]
EOF




Step 3.3 — Build image
-------------------------------------------
docker build -t university-portal:1 .


Step 3.4 — Run container
-------------------------------------------
docker run --rm --name uniportal -p 5000:5000 university-portal:1



Step 3.5 — Crash demo (container will stop because PID 1 dies)
-------------------------------------------
  Open:  http://SERVER_IP:5000/crash
✅ Terminal running Docker should exit → container stops.


Restart quickly:
docker run --rm --name uniportal -p 5000:5000 university-portal:1








******************************************
4) Kubernetes (self-healing + HPA + rollback) 
******************************************
4-node minikube cluster 
(✅ 1 control-plane + 3 workers) 

the workers as:
    worker-1 = butwal   portal-m02
    worker-2 = chitwan  portal-m03
    worker-3 = dang     portal-m04

    
portal, portal-m02, portal-m03, portal-m04


-------------------------------------------









-------------------------------------------









-------------------------------------------









-------------------------------------------









-------------------------------------------









-------------------------------------------









-------------------------------------------









-------------------------------------------






