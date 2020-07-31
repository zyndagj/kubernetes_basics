Exposing services
=================

The ``kubectl expose`` command creates a *service* for existing pods.
A *service* is a stable address for a pod or deployment.

A *service* is always required to make an external connection, and once created, ``kube-dns`` will allow us to resolve it by name (i.e. after creating service `hello`, the name `hello` will resolve to something).

Basic service types
-------------------

ClusterIP (default type)
   A virtual IP address is allocated for the service (in an internal, private range), which is reachable only from within the cluster (nodes and pods). Code can connect to the service using the original port number.
NodePort
   A port is allocated for the service (by default, in the 30000-32768 range) that port is made available on all our nodes and anybody can connect to it. Code must be configured to connect to that new port number
LoadBalancer
   An external load balancer is allocated for the service, and sends traffic to a ``NodePort``.
ExternalName
   The DNS entry managed by ``kube-dns`` will just be a `CNAME` to a provided record. No port, no IP address, no nothing else is allocated.

Exposing a port
---------------

The docker container `gzynda/sleepy-server <https://hub.docker.com/r/gzynda/sleepy-server>`_ serves a webpage on a specified port after sleeping a specified number of seconds.
The configuration file `sleepy.yaml <https://github.com/zyndagj/kubernetes_basics/blob/master/config/sleepy.yaml>`_ creates a deployment and exposes it outside the cluster on port 80.
It then creates the ``sleepy-svc`` *service* to expose port 80 of the deployment to the outside world.

.. literalinclude:: ../configs/sleepy.yaml
   :language: yaml
   :linenos:

After getting the external port (after 80) with

.. image:: ./images/external.png
   :target: ./images/external.png
   :align: center
   :alt: Log in with Docker Hub

Paste both the URL and PORT into your web browser in the URL:PORT format to view the running webpage from this deployment.

You'll notice that the webpage displays the name of the host it is being served from, sleeps for half a second, and then finishes printing "Hello World!".
You can stress-test the performance of this server with `seige <https://www.joedog.org/siege-manual/>`_ using 1 worker (``-c1``), 0 delay (``-d0``), and 10 tries (``-r10``).

::

   docker run --rm -t yokogawa/siege -d0 -r10 -c1 [node2 IP]:8080


### Running containers with open ports

* Since ping doesn't have anything to connect to, we'll have to run something else

* Start a bunch of ElasticSearch containers:
```.term1
kubectl run elastic --image=elasticsearch:2 --replicas=4
```

* Watch them being started:

  ```.term1
  kubectl get pods -w
  ```

The `-w` option "watches" events happening on the specified resources.

Note: please DO NOT call the service `search`. It would collide with the TLD.

### Exposing our deployment

* We'll create a default `ClusterIP` service

* Expose the ElasticSearch HTTP API port:

  ```.term1
  kubectl expose deploy/elastic --port 9200
  ```

* Look up which IP address was allocated:

  ```.term1
  kubectl get svc
  ```

### Services are layer 4 constructs

* You can assign IP addresses to services, but they are still *layer 4* (i.e. a service is not an IP address; it's an IP address + protocol + port)

* This is caused by the current implementation of `kube-proxy` (it relies on mechanisms that don't support layer 3)

* As a result: *you have to* indicate the port number for your service

* Running services with arbitrary port (or port ranges) requires hacks (e.g. host networking mode)

### Testing our service

* We will now send a few HTTP requests to our ElasticSearch pods

* Let's obtain the IP address that was allocated for our service, *programatically*:

  {% raw %}
  ```.term1
  IP=$(kubectl get svc elastic -o go-template --template '{{ .spec.clusterIP }}')
  ```
  {% endraw %}

* Send a few requests:

  ```.term1
  curl http://$IP:9200/
  ```

Our requests are load balanced across multiple pods.

### Clean up

* We're done with the `elastic` deployment, so let's clean it up

  ```.term1
  kubectl delete deploy/elastic
  ```

## Our app on Kube

### What's on the menu?
In this part, we will:

  * **build** images for our app,

  * **ship** these images with a registry,

  * **run** deployments using these images,

  * expose these deployments so they can communicate with each other,

  * expose the web UI so we can access it from outside.

### The plan
* Build on our control node (`node1`)

* Tag images so that they are named `$USERNAME/servicename`

* Upload them to a Docker Hub

* Create deployments using the images

* Expose (with a `ClusterIP`) the services that need to communicate

* Expose (with a `NodePort`) the WebUI

### Setup

* In the first terminal, set an environment variable for your [Docker Hub](https://hub.docker.com) user name. It can be the same [Docker Hub](https://hub.docker.com) user name that you used to log in to the terminals on this site.

  ```
  export USERNAME=YourUserName
  ```

* Make sure you're still in the `dockercoins` directory.

  ```.term1
  pwd
  ```

### A note on registries

* For this workshop, we'll use [Docker Hub](https://hub.docker.com). There are a number of other options, including two provided by Docker.

* Docker also provides:
  * [Docker Trusted Registry](https://docs.docker.com/datacenter/dtr/2.4/guides/) which adds in a lot of security and deployment features including security scanning, and role-based access control.
  * [Docker Open Source Registry](https://docs.docker.com/registry/).

### Docker Hub

* [Docker Hub](https://hub.docker.com) is the default registry for Docker.

  * Image names on Hub are just `$USERNAME/$IMAGENAME` or `$ORGANIZATIONNAME/$IMAGENAME`.

  * [Official images](https://docs.docker.com/docker-hub/official_repos/) can be referred to as just `$IMAGENAME`.

  * To use Hub, make sure you have an account. Then type `docker login` in the terminal and login with your username and password.

* Using Docker Trusted Registry, Docker Open Source Registry is very similar.

  * Image names on other registries are `$REGISTRYPATH/$USERNAME/$IMAGENAME` or `$REGISTRYPATH/$ORGANIZATIONNAME/$IMAGENAME`.

  * Login using `docker login $REGISTRYPATH`.

### Building and pushing our images

<!-- TODO: Fix default registry URL to username in dockercoins.yml -->
* We are going to use a convenient feature of Docker Compose

* Go to the `stacks` directory:

  ```.term1
  cd ~/dockercoins/stacks
  ```

* Build and push the images:

  ```.term1
  docker-compose -f dockercoins.yml build
  docker-compose -f dockercoins.yml push
  ```

Let's have a look at the dockercoins.yml file while this is building and pushing.

```
version: "3"
services:
  rng:
    build: dockercoins/rng
    image: ${USERNAME}/rng:${TAG-latest}
    deploy:
      mode: global
  ...
  redis:
    image: redis
  ...
  worker:
    build: dockercoins/worker
    image: ${USERNAME}/worker:${TAG-latest}
    ...
    deploy:
      replicas: 10
```

> Just in case you were wondering ... Docker "services" are not Kubernetes "services".

### Deploying all the things
* We can now deploy our code (as well as a redis instance)

* Deploy `redis`:

  ```.term1
  kubectl run redis --image=redis
  ```

* Deploy everything else:

  ```.term1
  for SERVICE in hasher rng webui worker; do
    kubectl run $SERVICE --image=$USERNAME/$SERVICE -l app=$SERVICE
  done
```

### Is this working?
* After waiting for the deployment to complete, let's look at the logs!

* (Hint: use `kubectl get deploy -w` to watch deployment events)

* Look at some logs:

  ```.term1
  kubectl logs deploy/rng
  kubectl logs deploy/worker
  ```

🤔 `rng` is fine ... But not `worker`.

💡 Oh right! We forgot to `expose`.

### Exposing services

### Exposing services internally

* Three deployments need to be reachable by others: `hasher`, `redis`, `rng`

* `worker` doesn't need to be exposed

* `webui` will be dealt with later

* Expose each deployment, specifying the right port:

  ```.term1
  kubectl expose deployment redis --port 6379
  kubectl expose deployment rng --port 80
  kubectl expose deployment hasher --port 80
  ```

### Is this working yet?
* The `worker` has an infinite loop, that retries 10 seconds after an error

* Stream the worker's logs:

  ```.term1
  kubectl logs deploy/worker --follow
  ```

(Give it about 10 seconds to recover)

* We should now see the `worker`, well, working happily.

### Exposing services for external access

* Now we would like to access the Web UI

* We will expose it with a `NodePort` (just like we did for the registry)

* Create a `NodePort` service for the Web UI:

  ```.term1
  kubectl create service nodeport webui --tcp=80 --node-port=30001
  ```

* Check the port that was allocated:

  ```.term1
  kubectl get svc
  ```

### Accessing the web UI

* We can now connect to *any node*, on the allocated node port, to view the web UI

Click on [this link](/){:data-term=".term2"}{:data-port="30001"}

*Alright, we're back to where we started, when we were running on a single node!*

## Security implications of `kubectl apply`

* When we do `kubectl apply -f <URL>`, we create arbitrary resources

* Resources can be evil; imagine a `deployment` that ...

  * starts bitcoin miners on the whole cluster

  * hides in a non-default namespace

  * bind-mounts our nodes' filesystem

  * inserts SSH keys in the root account (on the node)

  * encrypts our data and ransoms it

  * ☠️☠️☠️

### `kubectl apply` is the new `curl | sh`
* `curl | sh` is convenient

* It's safe if you use HTTPS URLs from trusted sources

* `kubectl apply -f` is convenient

* It's safe if you use HTTPS URLs from trusted sources

* It introduces new failure modes

* Example: the official setup instructions for most pod networks

## Scaling a deployment

* We will start with an easy one: the `worker` deployment

  ```.term1
  kubectl get pods

  kubectl get deployments
  ```

* Now, create more `worker` replicas:

  ```.term1
  kubectl scale deploy/worker --replicas=10
  ```

* After a few seconds, the graph in the web UI should show up. (And peak at 10 hashes/second, just like when we were running on a single one.)

## Daemon sets

* What if we want one (and exactly one) instance of rng per node?

* If we just scale deploy/rng to 2, nothing guarantees that they spread

* Instead of a deployment, we will use a daemonset

* Daemon sets are great for cluster-wide, per-node processes:

  * kube-proxy
  * weave (our overlay network) <!--Calico?-->
  * monitoring agents
  * hardware management tools (e.g. SCSI/FC HBA agents)
  * etc.

* They can also be restricted to run [only on some nodes](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/#running-pods-on-only-some-nodes).

### Creating a daemon set

* Unfortunately, as of Kubernetes 1.9, the CLI cannot create daemon sets

* More precisely: it doesn't have a subcommand to create a daemon set

* But any kind of resource can always be created by providing a YAML description:

  ```
  kubectl apply -f foo.yaml
  ```

* How do we create the YAML file for our daemon set?

  * option 1: read the docs
  * option 2: `vi` our way out of it

### Creating the YAML file for our daemon set
* Let's start with the YAML file for the current `rng` resource

* Dump the rng resource in YAML:

  ```.term1
  kubectl get deploy/rng -o yaml --export >rng.yml
  ```

Edit `rng.yml`

Note: `--export` will remove "cluster-specific" information, i.e.:

namespace (so that the resource is not tied to a specific namespace)
status and creation timestamp (useless when creating a new resource)
resourceVersion and uid (these would cause... *interesting* problems)

### "Casting" a resource to another
* What if we just changed the `kind` field?

* (It can't be that easy, right?)

Change `kind: Deployment` to `kind: DaemonSet`

Save, quit

Try to create our new resource:

  ```.term1
  kubectl apply -f rng.yml
  ```

* We all knew this couldn't be that easy, right!

### Understanding the problem

* The core of the error is:

  ```
  error validating data:
  [ValidationError(DaemonSet.spec):
  unknown field "replicas" in io.k8s.api.extensions.v1beta1.DaemonSetSpec,
  ...
  ```

* *Obviously*, it doesn't make sense to specify a number of replicas for a daemon set

* Workaround: fix the YAML

  * remove the `replicas` field
  * remove the `strategy` field (which defines the rollout mechanism for a deployment)
  * remove the `status: {}` line at the end

* Or, we could also ...

### Use the `--force`, Luke

* We could also tell Kubernetes to ignore these errors and try anyway

* The `--force` flag actual name is `--validate=false`

* Try to load our YAML file and ignore errors:

  ```.term1
  kubectl apply -f rng.yml --validate=false
  ```

Use the --force, Luke
We could also tell Kubernetes to ignore these errors and try anyway

The --force flag actual name is --validate=false

Try to load our YAML file and ignore errors:
kubectl apply -f rng.yml --validate=false
🎩✨🐇

Wait ... Now, *can* it be that easy?

### Checking what we've done

* Did we transform our `deployment` into a `daemonset`?

* Look at the resources that we have now:

  ```.term1
  kubectl get all
  ```

We have both `deploy/rng` and `ds/rng` now!

And one too many pods...

### Explanation

* You can have different resource types with the same name (i.e. a *deployment* and a *daemonset* both named `rng`)

* We still have the old `rng` *deployment*

* But now we have the new `rng` *daemonset* as well

* If we look at the pods, we have:

  * *one pod* for the deployment
  * *one pod per node* for the daemonset

### What are all these pods doing?
* Let's check the logs of all these `rng` pods

* All these pods have a `run=rng` label:

  * the first pod, because that's what `kubectl run` does
  * the other ones (in the daemon set), because we *copied the spec from the first one*

* Therefore, we can query everybody's logs using that `run=rng` selector

* Check the logs of all the pods having a label `run=rng`:

  ```.term1
  kubectl logs -l run=rng --tail 1
  ```

* It appears that *all the pods* are serving requests at the moment.

### Removing the first pod from the load balancer

* What would happen if we removed that pod, with `kubectl delete pod ...`?

  The replicaset would re-create it immediately.

* What would happen if we removed the `run=rng` label from that pod?

  The `replicaset` would re-create it immediately.

  ... Because what matters to the `replicaset` is the number of pods *matching that selector*.

* But but but ... Don't we have more than one pod with `run=rng` now?

  The answer lies in the exact selector used by the `replicaset` ...

### Deep dive into selectors
* Let's look at the selectors for the `rng` *deployment* and the associated *replica set*

* Show detailed information about the `rng` deployment:

  ```.term1
  kubectl describe deploy rng
  ```

* Show detailed information about the `rng` replica:

  ```
  kubectl describe rs rng-yyyy
  ```

* The replica set selector also has a `pod-template-hash`, unlike the pods in our daemon set.

## Updating a service through labels and selectors

* What if we want to drop the `rng` deployment from the load balancer?

* Option 1:

  * destroy it

* Option 2:

  * add an extra *label* to the daemon set
  * update the service *selector* to refer to that *label*

Of course, option 2 offers more learning opportunities. Right?

### Add an extra label to the daemon set

* We will update the daemon set "spec"

* Option 1:

  * edit the `rng.yml` file that we used earlier
  * load the new definition with `kubectl apply`

* Option 2:

  * use `kubectl edit`

*If you feel like you got this, feel free to try directly. We've included a few hints on the next slides for your convenience!*

### We've put resources in your resources
* Reminder: a daemon set is a resource that creates more resources!

* There is a difference between:

  * the label(s) of a resource (in the `metadata` block in the beginning)
  * the selector of a resource (in the `spec` block)
  * the label(s) of the resource(s) created by the first resource (in the `template` block)

* You need to update the selector and the template (metadata labels are not mandatory)

* The template must match the selector (i.e. the resource will refuse to create resources that it will not select)

### Adding our label
Let's add a label `isactive: yes`

In YAML, yes should be quoted; i.e. `isactive: "yes"`

* Update the daemon set to add `isactive: "yes"` to the selector and template label:

  ```.term1
  kubectl edit daemonset rng
  ```

  ```
  spec:
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: rng
        isactive: "yes"
    template:
      metadata:
        creationTimestamp: null
        labels:
          app: rng
          isactive: "yes"
  ```

* Update the service to add `isactive: "yes"` to its selector:

  ```.term1
  kubectl edit service rng
  ```

### Checking what we've done
* Check the logs of all `run=rng` pods to confirm that only 2 of them are now active:

  ```.term1
  kubectl logs -l run=rng
  ```

* The timestamps should give us a hint about how many pods are currently receiving traffic.

* Look at the pods that we have right now:

  ```.term1
  kubectl get pods
  ```

### More labels, more selectors, more problems?
* Bonus exercise 1: clean up the pods of the "old" daemon set

* Bonus exercise 2: how could we have done this to avoid creating new pods?

## Rolling updates

* By default (without rolling updates), when a scaled resource is updated:

  * new pods are created
  * old pods are terminated
  * ... all at the same time
  * if something goes wrong, ¯\_(ツ)_/¯

* With rolling updates, when a resource is updated, it happens progressively

* Two parameters determine the pace of the rollout: `maxUnavailable` and `maxSurge`

* They can be specified in absolute number of pods, or percentage of the `replicas` count

* At any given time ...

  * there will always be at least `replicas`-`maxUnavailable` pods available
  * there will never be more than `replicas`+`maxSurge` pods in total
  * there will therefore be up to `maxUnavailable`+`maxSurge` pods being updated

* We have the possibility to rollback to the previous version (if the update fails or is unsatisfactory in any way)

### Rolling updates in practice
* As of Kubernetes 1.8, we can do rolling updates with:

  `deployments`, `daemonsets`, `statefulsets`

* Editing one of these resources will automatically result in a rolling update

* Rolling updates can be monitored with the `kubectl rollout` subcommand

### Building a new version of the `worker` service

* Edit `dockercoins/worker/worker.py`, update the sleep line to sleep 1 second

* Go to the stack directory:

  ```.term1
  cd stacks
  ```

* Build a new tag and push it to the registry:

  ```.term1
    export TAG=v0.2
    docker-compose -f dockercoins.yml build
    docker-compose -f dockercoins.yml push
  ```

### Rolling out the new worker service

* Let's monitor what's going on by opening a few terminals, and run:

  ```.term1
    kubectl get pods -w
    kubectl get replicasets -w
    kubectl get deployments -w
  ```

* Update worker either with kubectl edit, or by running:

  ```.term1
  kubectl set image deploy worker worker=$USERNAME/worker:$TAG
  ```

* That rollout should be pretty quick. What shows in the web UI?

### Rolling out an error

* What happens if we make a mistake?

* Update worker by specifying a non-existent image:

  ```.term1
  export TAG=v0.3
  kubectl set image deploy worker worker=$REGISTRY/worker:$TAG
  ```

* Check what's going on:

  ```.term1
  kubectl rollout status deploy worker
  ```

* Our rollout is stuck. However, the app is not dead (just 10% slower).

### Recovering from a bad rollout

* We could push some v0.3 image (the pod retry logic will eventually catch it and the rollout will proceed)

* Or we could invoke a manual rollback

* Cancel the deployment and wait for the dust to settle down:

  ```.term1
  kubectl rollout undo deploy worker
  kubectl rollout status deploy worker
  ```

### Changing rollout parameters

* We want to:

  * revert to `v0.1` (which we now realize we didn't tag - yikes!)
  * be conservative on availability (always have desired number of available workers)
  * be aggressive on rollout speed (update more than one pod at a time)
  * give some time to our workers to "warm up" before starting more

* The corresponding changes can be expressed in the following YAML snippet:

  ```
  spec:
    template:
      spec:
        containers:
        - name: worker
          image: $USERNAME/worker:latest
    strategy:
      rollingUpdate:
        maxUnavailable: 0
        maxSurge: 3
    minReadySeconds: 10
  ```

### Applying changes through a YAML patch

* We could use `kubectl edit deployment worker`

* But we could also use `kubectl patch` with the exact YAML shown before

* Apply all our changes and wait for them to take effect:

  ```.term1
  kubectl patch deployment worker -p "
  spec:
    template:
      spec:
        containers:
        - name: worker
          image: $USERNAME/worker:latest
    strategy:
      rollingUpdate:
        maxUnavailable: 0
        maxSurge: 3
    minReadySeconds: 10
  "
  kubectl rollout status deployment worker
  ```

### Next steps
*Alright, how do I get started and containerize my apps?*

Suggested containerization checklist:

  * write a Dockerfile for one service in one app
  * write Dockerfiles for the other (buildable) services
  * write a Compose file for that whole app
  * make sure that devs are empowered to run the app in containers
  * set up automated builds of container images from the code repo
  * set up a CI pipeline using these container images
  * set up a CD pipeline (for staging/QA) using these images

And *then* it is time to look at orchestration!

### Namespaces

* Namespaces let you run multiple identical stacks side by side

* Two namespaces (*e.g.* `blue` and `green`) can each have their own `redis` service

* Each of the two `redis` services has its own `ClusterIP`

* `kube-dns` creates two entries, mapping to these two `ClusterIP` addresses:

* `redis.blue.svc.cluster.local` and `redis.green.svc.cluster.local`

* Pods in the `blue` namespace get a *search suffix* of `blue.svc.cluster.local`

* As a result, resolving `redis` from a pod in the `blue` namespace yields the "local" `redis`

This does not provide *isolation*! That would be the job of network policies.

### Stateful services (databases etc.)
* As a first step, it is wiser to keep stateful services *outside* of the cluster

* Exposing them to pods can be done with multiple solutions:

* `ExternalName` services (`redis.blue.svc.cluster.local` will be a `CNAME` record)

* `ClusterIP` services with explicit `Endpoints` (instead of letting Kubernetes generate the endpoints from a selector)

* Ambassador services (application-level proxies that can provide credentials injection and more)

### Stateful services (second take)
* If you really want to host stateful services on Kubernetes, you can look into:

  * volumes (to carry persistent data)
  * storage plugins
  * persistent volume claims (to ask for specific volume characteristics)
  * stateful sets (pods that are *not* ephemeral)

### HTTP traffic handling

* *Services* are layer 4 constructs

* HTTP is a layer 7 protocol

* It is handled by *ingresses* (a different resource kind)

* Ingresses allow:

  * virtual host routing
  * session stickiness
  * URI mapping
  * and much more!

### Logging and metrics

* Logging is delegated to the container engine

* Metrics are typically handled with Prometheus

### Managing the configuration of our applications

* Two constructs are particularly useful: secrets and config maps

* They allow to expose arbitrary information to our containers

* **Avoid** storing configuration in container images (There are some exceptions to that rule, but it's generally a Bad Idea)

* **Never** store sensitive information in container images (It's the container equivalent of the password on a post-it note on your screen)

<!--TODO check slide 267, managing stacks. Docker EE handles that, should we mention other things? -->

### Cluster federation
<!--TODO: should we include? Docker EE doesn't do Cluster Federation -->
* Kubernetes master operation relies on etcd

* etcd uses the Raft protocol

* Raft recommends low latency between nodes

* What if our cluster spreads to multiple regions?

* Break it down in local clusters

* Regroup them in a cluster *federation*

* Synchronize resources across clusters

* Discover resources across clusters

### Developer experience

* I've put this last, but it's pretty important!

* How do you on-board a new developer?

  * What do they need to install to get a dev stack?
  * How does a code change make it from dev to prod?
  * How does someone add a component to a stack?
