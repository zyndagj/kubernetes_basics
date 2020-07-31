Conclusions
===========

At this point you have

* Created a 2-node Kubernetes cluster

   * 1 Orchestrator
   * 1 Worker

* Learned basic commands for interacting with Kubernetes

   * ``kubectl get``
   * ``kubectl log``
   * ``kubectl run``
   * ``kubectl apply``
   * ``kubectl delete``

* Deployed and inspected the log of a running pod

   * ``kubectl run [pod name] --image=[image] [args]``
   * ``kubectl logs pod/[pod name]``

* Created a deployment from a template

   * ``kubectl apply -f [template]``

* Scaled up the number of replica pods in your deployment to increase response throughput

   * ``kubectl scale --replicas=2 [deployment]``

Continuing your education
-------------------------

Kubernetes
++++++++++

:Documentation: https://kubernetes.io/docs/home/
:Tutorials: https://kubernetes.io/docs/tutorials/
:Cheat Sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/

TACC Tutorials
++++++++++++++

* `Reproducible Science <https://tacc-reproducible-science.readthedocs.io/en/latest/>`_
* `Containers <https://containers-at-tacc.readthedocs.io/en/latest/>`_
* `TAPIS API <https://tacc.github.io/summer-institute-2020-tapis/>`_
* `Workflow Automation <https://tacc-reproducible-automation.readthedocs.io/en/latest/>`_
