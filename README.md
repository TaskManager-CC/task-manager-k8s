# Manager de Task-uri Cloud-Native

O aplicatie de gestionare a task-urilor bazata pe microservicii, lansata pe Kubernetes. Dispune de o interfata hibrida Planificator Saptamanal / Kanban, autentificare JWT si stocare persistenta PostgreSQL.

![Version](https://img.shields.io/badge/version-v6.0-blue)
![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=flat&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)

## Arhitectura
Aplicatia este impartita in urmatoarele microservicii:
* **Serviciul de Task-uri (Frontend/Backend):** Gestioneaza logica de business si interfata utilizator (Flask).
* **Serviciul de Autentificare:** Gestioneaza inregistrarea si logarea prin JWT (Flask).
* **Baza de date:** Stocare persistenta (PostgreSQL).
* **Monitorizare si Unelte:** Prometheus, Grafana, Portainer si Adminer.

---

## Cerinte
Cerinte de instalare:
1.  **Docker Desktop** (cu Kubernetes activat)
2.  **Helm** (Manager de pachete pentru Kubernetes)
3.  **Git**

---

## Pornire Rapida (Instalare)

### 1. Clonarea Repository-ului
```bash
git clone https://github.com/TaskManager-CC/
cd <task-manager-k8s>
```

### 2. Porneste Kubernetes
Pornirea cluster-ului (prin Docker Desktop sau Minikube).
```bash
# pentru Minikube
minikube start
```
```bash
# pentru Docker Desktop
kubectl config use-context docker-desktop
```

### 3. Lansare cu Helm
Aceasta comanda unica lanseaza toate serviciile (Aplicatie, BD, Monitorizare) in cluster.
```bash
helm install task-manager ./helm-chart --namespace task-manager-ns --create-namespace
```

### 4. Verificarea lansarii
Cand toate pod-urile arata statusul `Running`:
```bash
kubectl get pods -n task-manager-ns --watch
```

---

## Accesarea Aplicatiei

Deoarece aplicatia ruleaza intr-un cluster securizat, trebuie deschise "tunele" (port-forward) pentru a accesa serviciile din browser.

**Urmatoarele comenzi vor fi rulate in terminal si feresterele se vor tine deschise:**

### 1. Aplicatia Principala si Autentificare
```bash
# Tab Terminal 1
kubectl port-forward -n task-manager-ns service/auth-service 30001:5000

# Tab Terminal 2
kubectl port-forward -n task-manager-ns service/task-service 30002:5001
```
👉 **URL Aplicatie:** [http://localhost:30002](http://localhost:30002)

---

### 2. Unelte Administrative (Optional)

**Manager Baza de Date (Adminer):**
```bash
kubectl port-forward -n task-manager-ns service/adminer-service 30003:8080
```
👉 **URL:** [http://localhost:30003](http://localhost:30003)
* **Sistem:** PostgreSQL
* **Server:** `postgres-service`
* **Utilizator:** `postgres`
* **Parola:** `password`
* **Baza de date:** `tasksdb`

**Management Cluster (Portainer):**
```bash
kubectl port-forward -n task-manager-ns service/portainer-service 30004:9000
```
👉 **URL:** [http://localhost:30004](http://localhost:30004)

**Monitorizare (Grafana):**
```bash
kubectl port-forward -n task-manager-ns service/grafana-service 30006:3000
```
👉 **URL:** [http://localhost:30006](http://localhost:30006)
* **User:** `admin`
* **Parola:** `admin`

---

## Dezinstalare

Pentru a sterge aplicatia si toate resursele create:
```bash
helm uninstall task-manager --namespace task-manager-ns
kubectl delete namespace task-manager-ns
```

---

## Dezvoltare Locala

1.  **Creeare venv:** `python -m venv venv`
2.  **Activare:** `.\venv\Scripts\activate` (Windows) sau `source venv/bin/activate` (Mac/Linux)
3.  **Instalare dependente:** `pip install flask flask-cors psycopg2-binary pyjwt requests`