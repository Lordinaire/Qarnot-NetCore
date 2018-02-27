#!/usr/bin/env python
import sys
import qarnot
 
# Build the full command line
dotnet_cmd = 'dotnet Rendering.dll test.jpg'
 
# Create a connection, from which all other objects will be derived
conn = qarnot.Connection('qarnot.conf')
 
# Create a task. The 'with' statement ensures that the task will be
# deleted in the end, to prevent tasks from continuing to run after
# a Ctrl-C for instance
task = conn.create_task('processing-image', 'docker-batch', 1)
 
# Store if an error happened during the process
error_happened = False
 
try:
    # Set the command to run when launching the container, by overriding a
    # constant.
    # Task constants are the main way of controlling a task's behaviour
    task.constants['DOCKER_REPO'] = 'microsoft/dotnet'
    task.constants['DOCKER_TAG'] = 'latest'
    task.constants['DOCKER_CMD'] = dotnet_cmd
 
    # Create a resource disk and add our input file.
    input_disk = conn.create_disk('processing-image-resource')
    input_disk.add_directory("bin")
    input_disk.add_file("test.jpg")
 
    # Attach the disk to the task
    task.resources.append(input_disk)
 
    # Submit the task to the Api, that will launch it on the cluster
    task.submit()
 
    # Wait for the task to be finished, and monitor the progress of its
    # deployment
    last_state = ''
    done = False
    while not done:
        if task.state != last_state:
            last_state = task.state
            print("** {}".format(last_state))
 
        # Wait for the task to complete, with a timeout of 5 seconds.
        # This will return True as soon as the task is complete, or False
        # after the timeout.
        done = task.wait(60)
 
        # Display fresh stdout / stderr
        sys.stdout.write(task.fresh_stdout())
        sys.stderr.write(task.fresh_stderr())
 
    if task.state == 'Failure':
        # Display errors on failure
        print("** Errors: %s" % task.errors[0])
        error_happened = True
    else:
        # Or download the results
        task.download_results('.')
 
finally:
    task.delete(purge_resources=True, purge_results=True)
    # Exit code in case of error
    if error_happened:
        sys.exit(1)