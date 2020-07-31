Basic Kubernetes commands
=========================

On your orchestrator node (node1), lets run through the following commands to learn about what they do.

Kubernetes Terminology
----------------------

:Pod: Smallest deployable unit. Consists of 1 or more containers. Kind of like “localhost”.
:Deployment: Multiple pods.
:Service: Expose a pod or deployment to network.
:Volume: Attach storage.
:Namespace: Permissions-based grouping of objects.
:Job: Run a container to completion.

And more not covered today:

:ConfigMap: Store strings or files for pods to use.
:Secret: Encrypted configmap.
:Ingress: Expose HTTP+S routes to the network. Like a HTTP-specific Service.
:DaemonSet, ReplicaSet, LoadBalancer, etc.: More ways to do things.

Kubernetes commands
-------------------

Listing
+++++++

Listing nodes
   ::

      kubectl get nodes

Listing everything
   ::

      kubectl get all --all-namespaces


The main program for interacting with Kubernetes is ``kubectl``, which is a CLI tool that talks to the Kubernetes API.

.. note::

   You can also use ``--kubeconfig`` to pass a whole config to ``kubectl``

Getting information
-------------------

Information can be queried with the ``kubectl get`` command.
Which can query resources like nodes

::

   kubectl get nodes

and auto-complete to the best matching target

::

   kubectl get no
   kubectl get node

You can also increase the amount of information with the ``-o wide`` argument

::

   kubectl get nodes -o wide

or output in standardized formats like:

* JSON ``-o json``
* YAML ``-o yaml``

.. note::

   Outputting information to JSON is useful since it allows you to query information with ``jq``

   ::

      kubectl get nodes -o json | jq ".items[] | {name:.metadata.name} + .status.capacity"

Viewing details
---------------

The ``kubectl get`` command is great for listing resources, but details about each specific item can also be returned with ``kubectl describe`` which is used with the format

::

   kubectl describe [type]/[name]
   kubectl describe [type] [name]

We can get information about **node1** with

::

   kubectl describe node node1

You can also get an explanation about different *types* of resources with

::

   kubectl explain [type]

   # What is a node?
   kubectl explain node
   # What is a service?
   kubectl explain service

Exploring deployments
---------------------

Services
++++++++

A service is a pod or deployment exposed to a network.
We can see that our cluster already has the API service running with

::

   kubectl get services

A ClusterIP service is internal, meaning that it's only available from inside the cluster.

.. note::

   The API requires authentication, so it returns a 403 error if you try to connect.

   ::

      # Assuming this is the IP of your Kubernetes service
      curl -k https://10.96.0.1

Running containers
++++++++++++++++++

Containers are manipulated through pods, and a pod is a group of containers:

* running together (on the same node)
* sharing resources (RAM, CPU; but also network, volumes)

Running pods can be listed with

::

   kubectl get pods


You'll quickly find that there are no pods running in the default namespace.

Namespaces
++++++++++

Namespaces are a way to separate resources by named tag.
Namespaces can be listed with

::

   kubectl get namespaces

When we looked for pods, we queried the "default" namespace.
We list pods running in specific name spaces with the ``-n`` argument.

::

   kubectl -n kube-system get pods

.. note::

   Information about these services can be found `here <https://kubernetes.io/docs/concepts/overview/components/#control-plane-components>`_.
   The ``READY`` column indicates the number of containers in each pod, and pods with a name ending with ``-node`` are the main components (they have been specifically "pinned" to the orchestrator node)
