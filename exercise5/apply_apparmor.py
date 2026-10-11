
import docker

client = docker.from_env()

try:
    print("Building image from Dockerfile...")
    image, build_logs = client.images.build(
        path=".",
        tag="flask-apparmor"
    )
    print("Image built successfully.")

    print("\nRunning container with AppArmor profile...")

    container = client.containers.run(
        "flask-apparmor",
        ports={"5000/tcp": 5001},
        security_opt=["apparmor=my-apparmor-profile"],
        detach=True,
    )

    try:
        print(f"Container started: {container.short_id}")

        info = client.api.inspect_container(container.id)
        print("\nContainer AppArmor profile:")
        print(f"AppArmorProfile: {info.get('AppArmorProfile')}")

        print("\nRequested security options:")
        print(info["HostConfig"].get("SecurityOpt"))

        container.reload()
        print(f"\nContainer status: {container.status}")

    finally:
        print("\nStopping and removing test container...")
        container.stop()
        container.remove()
        print("Container stopped and removed.")

except docker.errors.DockerException as error:
    print(f"Docker error: {error}")
