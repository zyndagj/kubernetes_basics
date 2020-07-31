Introduction
============

This tutorial will guide you through basic Kubernetes features and concepts.

Kubernetes concepts
-------------------
Kubernetes is a container management system

It runs and manages containerized applications on a cluster

What does that really mean?

Basic things we can ask Kubernetes to do
++++++++++++++++++++++++++++++++++++++++
Start 5 containers using image atseashop/api:v1.3

Place an internal load balancer in front of these containers

Start 10 containers using image atseashop/webfront:v1.3

Place a public load balancer in front of these containers

It’s Black Friday (or Christmas), traffic spikes, grow our cluster and add containers

New release! Replace my containers with the new image atseashop/webfront:v1.4

Keep processing requests during the upgrade; update my containers one at a time

Other things that Kubernetes can do for us
++++++++++++++++++++++++++++++++++++++++++
Basic autoscaling

Blue/green deployment, canary deployment

Long running services, but also batch (one-off) jobs

Overcommit our cluster and evict low-priority jobs

Run services with stateful data (databases etc.)

Fine-grained access control defining what can be done by whom on which resources

Integrating third party services (service catalog)

Automating complex tasks (operators)

Module Learning Objectives
--------------------------

This module will be fully interactive.
Participants are **strongly encouraged** to follow along on the command line.
After completing this module, participants should be able to:

* Create a python package hosted on GitHub
* Specify package dependencies
* Create tests to validate package
* Understand the importance of random seeds and deterministic testing
* Install package with pip from GitHub

Why is this important?
----------------------

Python is often thought as a scripting language, and used in a similar manner to bash.
While this is true, many python scripts require third-party packages, and there is often no way to know if the script actually functions as expected on your system.

If you plan on sharing your script with others, we recommend transforming it into a proper package with specified dependencies and validation tests.
This precaution will improve reproducibility and help you avoid the "works on my system" issues you encounter while supporting your community.

Requirements
------------

* Accounts

  * `Docker Hub <https://hub.docker.com>`_
