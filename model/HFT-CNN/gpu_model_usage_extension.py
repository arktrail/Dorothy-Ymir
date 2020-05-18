from chainer import training
import nvidia_smi
import cupy


class GPUModelUsage(training.Extension):
    def __init__(self):
        # print("init the GPUModelUsage")
        nvidia_smi.nvmlInit()
        #  self.handles = nvidia_smi.nvmlDeviceGetHandleByIndex(-1)
        #  self.handles = nvidia_smi.XmlDeviceQuery()
        self.handles0 = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
        self.handles1 = nvidia_smi.nvmlDeviceGetHandleByIndex(1)

        self.mempool = cupy.get_default_memory_pool()
        self.pinned_mempool = cupy.get_default_pinned_memory_pool()

        self.device0 = cupy.cuda.Device(0)
        self.device1 = cupy.cuda.Device(1)

    def __call__(self, trainer):
        pass
        #print("cupy memory pool operation")
        #print("cupy: mempool used GB: {}".format(
        #    self.mempool.used_bytes() / (1024 ** 2)))
        #print("cupy: mempool total GB: {}".format(
        #    self.mempool.total_bytes() / (1024 ** 2)))
        #print("cupy: pinned_mempool n_free_blocks(): {}".format(
        #    self.pinned_mempool.n_free_blocks()))

        # usage in GiB
        #  print(f'device0 mem: {self.device0.mem_info.used / (1024**2)} (GiB)')
        #  print(
        #  f'device0 mem: {100 * (self.device0.mem_info.used / self.device0.mem_info.total):.3f}%')
        #  print(f'device1 mem: {self.device1.mem_info.used / (1024**2)} (GiB)')
        #  print(
        #  f'device1 mem: {100 * (self.device1.mem_info.used / self.device1.mem_info.total):.3f}%')

        #print("cupy: device0 cuda free mem: {} (GB), total mem: {} (GB)".format(
        #    self.device0.mem_info[0] / (1024 ** 2), self.device0.mem_info[1] / (1024 ** 2)))
        #print("cupy: device1 cuda free mem: {} (GB), total mem: {} (GB)".format(
        #    self.device1.mem_info[0] / (1024 ** 2), self.device1.mem_info[1] / (1024 ** 2)))

        #  mem_res = nvidia_smi.nvmlDeviceGetMemoryInfo(self.handles0)
        #  print('handle 0')
        #  print(f'mem: {mem_res.used / (1024**2)} (GiB)')  # usage in GiB
        #  # percentage
        #  print(f'mem: {100 * (mem_res.used / mem_res.total):.3f}%')

        #  mem_res = nvidia_smi.nvmlDeviceGetMemoryInfo(self.handles1)
        #  print('handle 1')
        #  print(f'mem: {mem_res.used / (1024**2)} (GiB)')  # usage in GiB
        #  # percentage
        #  print(f'mem: {100 * (mem_res.used / mem_res.total):.3f}%')
