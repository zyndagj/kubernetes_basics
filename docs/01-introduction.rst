Introduction
============

This tutorial will guide you through basic Kubernetes features and concepts.

Module Learning Objectives
--------------------------

This module will be fully interactive.
Participants are **strongly encouraged** to follow along on the command line.
After completing this module, participants should be able to:

* Create a 2-node Kubernetes cluster
* Learn basic commands for interacting with Kubernetes
* Deploy and inspect a running pod
* Create a templated deployment
* Scale a deployment
* Increase response throughput with a LoadBalancer

Why is this important?
----------------------

Similar to Docker Swarm, Kubernetes is a container management system.
It runs and manages containerized applications on a single system, or up to 5000 nodes in a distributed cluster.

Kubernetes enables many sophisticated features through simple templating:

* Basic autoscaling
* Long-running and batch services
* Overcommit our cluster while also removeing low-priority jobs
* Run services with stateful data (databases etc.)
* Fine-grained permissions on resources
* Automating complex tasks (operators)

Utilizing Kubernetes will make your deployments both more reproducible, resilient, and performant.

Requirements
------------

* Accounts

  * `Docker Hub <https://hub.docker.com>`_
