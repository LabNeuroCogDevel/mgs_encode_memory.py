FROM gitpod/workspace-full-vnc:latest

# install dependencies
RUN apt-get update \
    && apt-get install -y twm xterm wget python \
    && apt-get clean && rm -rf /var/cache/apt/* && rm -rf /var/lib/apt/lists/* && rm -rf /tmp/* && \
    wget -O wxpython.whl "https://extras.wxpython.org/wxPython4/extras/linux/gtk3/debian-9/wxPython-4.0.6-cp27-cp27mu-linux_x86_64.whl" && \
    pip install psychopy wxpython.whl && \
    rm wxpython.whl
