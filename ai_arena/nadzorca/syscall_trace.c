#include <sys/reg.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <sys/syscall.h>
#include <sys/ptrace.h>
#include <sys/time.h>
#include <errno.h>

#if __WORDSIZE == 64
#define bits_num 8
#define syscall_place ORIG_RAX

#else
#define bits_num 4
#define syscall_place ORIG_EAX

#endif

#define fsn 22

int main(int argc, char **argv)
{
    int exec_status;
    int naughty_child;
    pid_t child;
    int status, syscall_nr, i;
    int forbidden_syscalls_number = fsn; 
    int forbidden_syscalls[fsn] = {
        //multiprocess kernel/process.c 4
        __NR_fork, __NR_clone, __NR_vfork, __NR_wait4,
        //open, directories fs/open.c  10
         __NR_creat, __NR_link, __NR_unlink, __NR_chdir, __NR_mknod, __NR_chmod, __NR_lchown, __NR_rmdir, __NR_rename, __NR_chroot,
        //system misc 9
        //__NR_mount, __NR_umount2,__NR_setuid, __NR_ptrace, __NR_sysinfo, __NR_getuid, __NR_setuid, __NR_getppid, __NR_reboot,
        //__NR_getuid,
        //pipes 6
        __NR_pipe, __NR_pipe2, __NR_dup, __NR_dup2, __NR_dup3, __NR_fcntl,
        //time 1
        __NR_utime,
        //net 12
        //__NR_shutdown, __NR_socket, __NR_socketpair, __NR_bind, __NR_listen, __NR_accept, __NR_connect, __NR_getsockname, __NR_getpeername,  __NR_recvfrom, 
        //__NR_sendmsg, __NR_recvmsg,
        //signals 1
        __NR_kill,
        //limits 1
        //__NR_setrlimit, //__NR_getrlimit,
        };
    int max_fsn = -1;
    for (i=0; i<fsn; ++i)
        if (forbidden_syscalls[i] > max_fsn)
            max_fsn = forbidden_syscalls[i];
    short illegal_syscall[max_fsn+1];
    for (i=0; i<= max_fsn; ++i)
        illegal_syscall[i] = 0;
    for (i=0; i<fsn; ++i)
        illegal_syscall[forbidden_syscalls[i]] = 1;
    child = fork();
    if (child == 0) {
        /* In child. */
        printf("%d\n", getpid());
        fflush(stdout);
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
        if (strcmp(argv[2], "PYTHON") == 0) {
            exec_status = execl("/usr/bin/python2.7", "/usr/bin/python2.7", "-u", argv[1], NULL);
        } else if (strcmp(argv[2], "C") == 0 || strcmp(argv[2], "CPP") == 0) {
            exec_status = execl(argv[1], argv[1], NULL);
        }
        if (exec_status == -1)
            fprintf(stderr, "Exec failure %d\n", errno);
    }
    else if (child < 0) {
        printf("%d\n", child);
        fflush(stdout);
        exit(EXIT_FAILURE);
    }
    else {
        /* In parent. */
        naughty_child = 0;

        ptrace(PTRACE_SYSCALL, child, NULL, NULL);
        while (1) {
            wait(&status);

            /* Abort loop if child has exited. */
            if (WIFEXITED(status) || WIFSIGNALED(status))
                break;
        
            /* Obtain syscall number from the child's process context. */
            syscall_nr = ptrace(PTRACE_PEEKUSER, child, bits_num * syscall_place, NULL);
        
            if (illegal_syscall[syscall_nr]) {
                fprintf(stderr ,"Program tried to use forbiden system call %d. Terminating program.\n", syscall_nr);
                ptrace(PTRACE_KILL, child, NULL, NULL);
            }
            else {
                ptrace(PTRACE_SYSCALL, child, NULL, NULL);
            }
        }
        exit(EXIT_SUCCESS);
    }
}

