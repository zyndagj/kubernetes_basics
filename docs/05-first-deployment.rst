First deployment
================

While running pods with ``kubectl run`` is both convenient and familiar, you have to use templated deployments to take advantage of advanced Kubernetes features.


Pingpong deployment
-------------------

We originally deployed the pingpong pod using

::

   kubectl run pingpong --image alpine ping 8.8.8.8

We can create a deployment with the same behavior by creating the `pingpong.yaml <https://github.com/zyndagj/kubernetes_basics/blob/master/config/pingpong.yaml>`_ config

.. literalinclude:: ../configs/pingpong.yaml
   :language: yaml
   :linenos:

and submitting it for deployment.

::

   kubectl apply -f pingpong.yaml

You'll notice that it created a deployment, replicaset, and a pod.

::

   kubectl get all

Scaling the deployment
----------------------

Now that our pingpong application is a proper deployment, we can scale it up with ``kubectl scale``

::

   kubectl scale --replicas=2 deployment.apps/pingpong

If you look at everything running, you'll see that there are now 2 replicas and 2 pods.

::

   kubectl get all

However, the longer running pod will have a longer output.
Each pod has a randomized name, so you'll need to fill in your own.

::

   kubectl logs [pod1] | wc -l
   kubectl logs [pod2] | wc -l

You can also view the last few lines of each pod's log by selecting by app

::

   kubectl logs -l app=ping-app --tail 1

Removing your deployment
------------------------

Once done, deployments are removed in the same way as pods, but all pods and replicasets will be removed as well.

::

   kubectl delete deployment.apps/pingpong
