#include <sys/reg.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <sys/syscall.h>
#include <sys/ptrace.h>

#if __WORDSIZE == 64
#define bits_num 8
#define syscall_place ORIG_RAX

#else
#define bits_num 4
#define syscall_place ORIG_EAX

#endif

int main(int argc, char **argv)
{
    int exec_status;
    int naughty_child;
    pid_t child;
    int status, syscall_nr, i;
    int forbidden_syscalls_number = 2; 
    int forbidden_syscalls[2] = {__NR_fork, __NR_clone};

    child = fork();
    if (child == 0) {
        /* In child. */
        printf("%d\n", getpid());
        fflush(stdout);
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
        if (strcmp(argv[2], "PYTHON") == 0) {
            exec_status = execl("/usr/bin/python2.6", "/usr/bin/python2.6", argv[1], NULL);
        } else if (strcmp(argv[2], "C") == 0 || strcmp(argv[2], "CPP") == 0) {
            exec_status = execl(argv[1], argv[1], NULL);
        }
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
        
            for (i=0; i<forbidden_syscalls_number; ++i) {
                if (syscall_nr == forbidden_syscalls[i]) {
                    printf("Child tried to use forbiden system call %d. Terminating child.\n", syscall_nr);
                    ptrace(PTRACE_KILL, child, NULL, NULL);
                    i = forbidden_syscalls_number;
                    naughty_child = 1;
                }
            }
            if (!naughty_child) {
                ptrace(PTRACE_SYSCALL, child, NULL, NULL);
            }
        }
        exit(EXIT_SUCCESS);
    }
}

