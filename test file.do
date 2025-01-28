The Jupyter Kernels category lists all Jupyter kernels that VS Code detects in the context of the compute system it’s operating in (your desktop, Codespaces, remote server, etc.). Each Jupyter kernel has a Jupyter kernel specification (or Jupyter kernelspec), which contains a JSON file (kernel.json) with details about the kernel—name, description, and CLI information required to launch a process as a kernel.

When the Visual Studio Code Jupyter extension is executing cells, it's using Jupyter kernels to execute the code and retrieve output to display in the notebook document. Users can install kernelspec files for different languages on their system. By installing them into the same locations as Jupyter they will get picked up by the Jupyter extension and should show up as options in the notebook kernel picker. These kernel will be shown in the kernel picker under the group label "Jupyter Kernel..."