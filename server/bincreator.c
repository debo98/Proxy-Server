#include <stdio.h>

int main() {
    /* Create the file */
    char x[100] = "HULOOOOOSd efjwebkjfn wekjfwkefh KWEHFKJHWAERKJF HAWKJ H FVKJW686+65 G IWEHFCKUWEHFVKJEWANFLKD HEWG" ; 
    FILE *fh = fopen ("file.bin", "wb");
    if (fh != NULL) {
        fwrite (&x, sizeof (x), 1, fh);
        fclose (fh);
    }

    /* Read the file back in */
    fh = fopen ("file.bin", "rb");
    if (fh != NULL) {
        fread (&x, sizeof (x), 1, fh);
        fclose (fh);
    }

    /* Check that it worked */
    printf ("Value is: %s\n", x);

    return 0;
}