Running our first pod
=====================

Just to be clear, Kubernetes runs "pods", not containers.

In this example we are going to:

1. Create a pod that happens to run a single alpine linux container
2. The container will run the ``ping``
3. We'll ping Google's public DNS (8.8.8.8)

Starting the pod
++++++++++++++++

Start the pod with ``kubectl run`` which will look similar to ``docker run``.

::

   kubectl run pingpong --image alpine ping 8.8.8.8


Kubernetes should only report that ``pod/pingpong`` was created.
You can confirm this by listing all running pods.

::

   kubectl get pods -o wide

It should have been started on our only worker node, node2.

Viewing output
++++++++++++++

If you remember, the ``ping`` command, by default, pings an address and prints the response time until it is terminated.
That means our pod is still printing to standard output somewhere on the cluster.
That output can be viewed with the ``kubectl logs [type]/[name]`` command.

::

   kubectl logs pod/pingpong

You can also select specific parts of the output with:

* ``--tail N`` - View the last N lines of output
  ::

     kubectl logs pod/pingpong --tail 3

* ``--since N[unit]`` - View logs since the last N hours (h), minutes (m), seconds (s)
  ::

     kubectl logs pod/pingpong --since 10s

* ``--follow`` - Upate the output in real time (similar to watch)
  ::

     kubectl logs pod/pingpong --tail 1 --follow

Deleting the pod
++++++++++++++++

Pods can be deleted with the ``kubectl delete`` command

::

   kubectl delete pod/pingpong
