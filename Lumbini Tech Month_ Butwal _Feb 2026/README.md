 
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

flask==3.0.3
gunicorn==22.0.0
werkzeug==3.0.3







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


(✅ 1 control-plane + 1 workers) 

    
controlplane:~$ kubectl get nodes
NAME           STATUS   ROLES           AGE   VERSION
controlplane   Ready    control-plane   13d   v1.34.3
node01         Ready    <none>          12d   v1.34.3







Step 4.1 — Create Kubernetes manifests
-------------------------------------------

apiVersion: apps/v1
kind: Deployment
metadata:
  name: uniportal
spec:
  replicas: 1
  revisionHistoryLimit: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: uniportal
  template:
    metadata:
      labels:
        app: uniportal
    spec:
      containers:
      - name: uniportal
        image: huma11994/university-portal:1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 5000
        env:
        - name: RUN_MODE
          value: "Kubernetes (replicas=1 for login)"
        - name: APP_SECRET
          value: "change-me"
        resources:
          requests:
            cpu: "150m"
            memory: "128Mi"
          limits:
            cpu: "400m"
            memory: "256Mi"
        readinessProbe:
          httpGet:
            path: /healthz
            port: 5000
          initialDelaySeconds: 2
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /healthz
            port: 5000
          initialDelaySeconds: 8
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: uniportal-svc
spec:
  selector:
    app: uniportal
  type: NodePort
  sessionAffinity: ClientIP
  ports:
  - name: http
    port: 80
    targetPort: 5000



kubectl apply -f uniportal.yaml

kubectl scale deployment uniportal --replicas 3


kubectl rollout status deployment/uniportal
kubectl get pods -o wide
kubectl get svc uniportal-svc






Step 4.2 — Scale to 3 replicas (HA + load balancing)
-------------------------------------------

kubectl scale deployment/uniportal --replicas=3
kubectl get pods -o wide


      Refresh /whoami multiple times → you’ll see 
      different pod hostnames.
      
      Crash one pod with /crash → service stays 
      up (other replicas serve) → crashed pod is recreated.








Step 4.4 — HPA (autoscale 3 → 10)
-------------------------------------------

4.1a Ensure metrics server works
---------------------------------
kubectl top nodes


If not available:

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml


Recheck:
    kubectl top nodes
    kubectl top pods



4.2 Create HPA
-----------------
cat > hpa.yaml <<'YAML'

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: uniportal-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: uniportal
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
    
YAML





kubectl apply -f hpa.yaml
kubectl get hpa
kubectl get hpa -w





4.3 Generate load
-----------------
kubectl run -it --rm loadgen --image=busybox:1.36 --restart=Never -- /bin/sh


Inside:
-----------------
while true; do wget -q -O- http://uniportal-svc/burn >/dev/null; done


In another terminal:

kubectl get pods -w
kubectl top pods


✅ HPA scales pods above 3.

Stop loadgen: Ctrl+C
-------------------------------------------





Step 4.3 — s
-------------------------------------------




Step 4.3 — s
-------------------------------------------




Step 4.3 — s
-------------------------------------------

-------------------------------------------









-------------------------------------------









-------------------------------------------









-------------------------------------------









-------------------------------------------









-------------------------------------------






