
import docker

client = docker.from_env()
container = None

try:
    container = client.containers.run(
        "flask-apparmor",
        ports={"5000/tcp": 5002},
        security_opt=["apparmor=my-apparmor-profile"],
        detach=True,
    )

    print(f"Container started: {container.short_id}")

    info = client.api.inspect_container(container.id)
    print("Container profile:", info.get("AppArmorProfile"))

    print("\nTest 1: Read /etc/passwd")
    code, output = container.exec_run(
        ["python", "-c", "open('/etc/passwd').read()"]
    )
    print(output.decode(errors="replace").strip())
    print("PASS: blocked" if code != 0 else "FAIL: readable")

    print("\nTest 2: Execute /bin/bash")
    try:
        code, output = container.exec_run(
            ["python", "-c",
             "import subprocess; subprocess.run(['/bin/bash', '-c', 'echo executed'], check=True)"]
        )
        print(output.decode(errors="replace").strip())
        print("Exit code:", code)
    except docker.errors.APIError as error:
        print("Execution was rejected:", error)

finally:
    if container is not None:
        try:
            container.stop()
        finally:
            container.remove(force=True)
        print("\nContainer cleaned up.")
