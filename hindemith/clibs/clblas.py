import ctypes as ct
import pycl as cl
import os

from hindemith.cl import queue

try:
    from sys import platform as _platform
    if _platform == "linux" or _platform == "linux2":
        ext = "so"
    elif _platform == "darwin":
        ext = "dylib"
    path = os.path.dirname(os.path.abspath(__file__))
    _clblaslib = ct.cdll.LoadLibrary(path + "/libclBLAS.{}".format(ext))
except OSError:
    raise Exception("Could not load clBLAS, build it with ./build_clBLAS.sh")

err = _clblaslib.clblasSetup()
if err:
    raise Exception("Error setting up clBLAS: {}".format(err))

_clblaslib.clblasSgemm.restype = ct.c_void_p
_clblaslib.clblasSgemm.argtypes = (
    ct.c_int, ct.c_int, ct.c_int, ct.c_size_t, ct.c_size_t, ct.c_size_t,
    ct.c_float, cl.cl_mem, ct.c_size_t, ct.c_size_t, cl.cl_mem, ct.c_size_t,
    ct.c_size_t, ct.c_float, cl.cl_mem, ct.c_size_t, ct.c_size_t, ct.c_size_t,
    ct.POINTER(cl.cl_command_queue), ct.c_size_t, ct.c_void_p, ct.c_void_p
)


def sgemm(transA, transB, alpha, A, A_offset, lda, B, B_offset, ldb, beta, C,
          C_offset, ldc, m, n, k, _queue=None, wait_for=None):
    if _queue is None:
        _queue = queue
    cblas_row_major = ct.c_int(0)
    transA = ct.c_int(1 if transA else 0)
    transB = ct.c_int(1 if transB else 0)
    lda = ct.c_size_t(int(lda))
    ldb = ct.c_size_t(int(ldb))
    ldc = ct.c_size_t(int(ldc))
    m = ct.c_size_t(int(m))
    n = ct.c_size_t(int(n))
    k = ct.c_size_t(int(k))
    alpha = ct.c_float(alpha)
    beta = ct.c_float(beta)
    if wait_for is None:
        num_wait = 0
    else:
        num_wait = 1
        wait_for = ct.byref(wait_for)
    done_evt = cl.cl_event()
    err = _clblaslib.clblasSgemm(cblas_row_major, transA, transB, m, n, k,
                                 alpha, A.ocl_buf, ct.c_size_t(A_offset), lda,
                                 B.ocl_buf, ct.c_size_t(B_offset), ldb, beta,
                                 C.ocl_buf, ct.c_size_t(C_offset), ldc,
                                 ct.c_size_t(1), ct.byref(_queue),
                                 ct.c_size_t(num_wait), wait_for,
                                 ct.byref(done_evt))
    if err:
        raise Exception("clBLAS sgemm returned error code {}".format(err))
    return done_evt


def sgemv(transA, M, N, alpha, bufA, offA, lda, bufX, offX, incx, beta, bufY,
          offY, incy, wait_for=None):
    cblas_row_major = ct.c_int(0)
    transA = ct.c_int(1 if transA else 0)
    lda = ct.c_size_t(int(lda))
    incx = ct.c_size_t(int(incx))
    incy = ct.c_size_t(int(incy))
    M = ct.c_size_t(int(M))
    N = ct.c_size_t(int(N))
    alpha = ct.c_float(alpha)
    beta = ct.c_float(beta)
    if wait_for is None:
        num_wait = 0
    else:
        num_wait = 1
    done_evt = cl.cl_event()
    err = _clblaslib.clblasSgemv(cblas_row_major, transA, M, N,
                                 alpha, bufA.ocl_buf, ct.c_size_t(offA), lda,
                                 bufX.ocl_buf, ct.c_size_t(offX), incx, beta,
                                 bufY.ocl_buf, ct.c_size_t(offY), incy,
                                 ct.c_size_t(1), ct.byref(queue),
                                 ct.c_size_t(num_wait), ct.byref(wait_for),
                                 ct.byref(done_evt))
    if err:
        raise Exception("clBLAS sgemv returned error code {}".format(err))
    return done_evt
