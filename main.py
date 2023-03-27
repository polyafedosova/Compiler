import os
import mel_parser


def main():
    prog = mel_parser.parse('''
    Console.ReadLine(w);    
    Console.WriteLine(12 + 6);
    int a;
    a = 12;
    double c = 12;
    class Main { 
        public int main(int a) { 
            int c = 0; 
        } 
    }
    if ((a > 12) && (b != 10)) { 
        return 12; 
    }
    while (a == b) { 
        if (a >= c) { 
            int a = 0;
            return c; 
        } 
    }
    for (int a = 0; a < 10; a == 12) { 
        if (a >= c) { 
            return c; 
        } 
    }
    ''')
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()

