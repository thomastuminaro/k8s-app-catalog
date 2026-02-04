import typer
from kube import Pod, list_all_namespace_pods
from pprint import pprint

app = typer.Typer()

""" @app.callback()
def main():
    typer.echo("Testing typer...") """

@app.command("create")
def create(resource_kind, name: str = typer.Option(help="What resource to create"),
            namespace : str = typer.Option("default", help="In what namespace do you need to create, as default will be default ns"),
            image : str = typer.Option("", help="If creating a pod, the image name")):
    '''
    Creating a k8s resource.
    '''
    if resource_kind == "pod":
        typer.echo(f"You will create pod {name} in namespace {namespace}...")
        pod = Pod(name=name, namespace=namespace)
        pod.create(cont_image=image)
    else:
        typer.echo("This feature is not yet implemented.")

@app.command("delete")
def delete(resource_kind, name: str = typer.Option(help="What resource to create"),
            namespace : str = typer.Option("default", help="In what namespace do you need to create, as default will be default ns")):
    '''
    Deleting a k8s resource.
    '''
    if resource_kind == "pod":
        typer.echo(f"You will delete pod {name} in namespace {namespace}...")
        pod = Pod(name=name, namespace=namespace)
        pod.delete()
    else:
        typer.echo("This feature is not yet implemented.")

@app.command("list")
def list_resources(resource_kind, namespace : str = typer.Option(help="What resource to list")):
    if resource_kind == "pod":
        for pod in list_all_namespace_pods(namespace=namespace):
            print(pod)

if __name__ == "__main__":
    app()