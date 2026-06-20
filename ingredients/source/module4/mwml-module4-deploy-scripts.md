# Module 4 · Made-With-ML — Deploy Scripts

> Source: `deploy/`. How the trained model is shipped: Anyscale/Ray cluster definitions, batch jobs, and the online serving deployment.

| File | Purpose | Infrastructure target | Student build task |
|---|---|---|---|
| `cluster_compute.yaml` | Defines the cloud environment, region, and compute instance types (head and GPU worker nodes) with AWS block device mappings. | Anyscale cluster on AWS | Configure the underlying virtual machines and AWS resources for the cluster. |
| `cluster_env.yaml` | Specifies the base Docker image, OS packages, and Python commands to set up the working environment. | Anyscale cluster environment | Define the Docker container and dependencies required to run the workload. |
| `jobs/workloads.sh` | Shell script orchestrating the end-to-end pipeline: data/code tests, training, extracting run ID, evaluation, model testing, and saving artifacts to S3. | Anyscale Ray job (AWS S3) | Execute the complete batch workflow from testing to training and artifact storage. |
| `jobs/workloads.yaml` | Anyscale job configuration mapping the entrypoint script to the custom cluster environment and compute resources. | Anyscale Ray jobs | Configure and submit the batch training job to the Ray cluster. |
| `services/serve_model.py` | Python script that retrieves model artifacts from S3, reads the run ID, and binds the `ModelDeployment` class to create the Ray Serve entrypoint. | Ray Serve | Implement the model retrieval and entrypoint binding for the Serve deployment. |
| `services/serve_model.yaml` | Ray Serve configuration linking the Python entrypoint to the cluster environment, setting runtime variables, and defining the rollout strategy. | Ray Serve (Anyscale) | Configure the online serving deployment and rollout strategy (ROLLOUT vs IN_PLACE). |
