from bin.export import program_info

ProgramName = "PCSMT (Plain Craft Server Management Terminal)"
PowerBy = "Power by Ksayus"
GithubPage = "--Github:\t\thttps://github.com/Ksayus/PCSMT-2"
GiteePage = "--Gitee:\t\thttps://gitee.com/Ksayus/PCSMT-2"
KsayusPage = "--Ksayus:\t\thttps://ksayus.github.io/2025/01/30/PCSMT-2/"
AuthorBilibiliPage = "--Bilibili:\t\thttps://space.bilibili.com/558271819"
PersonalWebsite = "--Personal Website:\thttps://ksayus.github.io"

def Homepage():
    print("-------------------------------")
    print("_____   _____  _____ __  __ _______     \t")
    print("|  __\ / ____|/  ___|  \/  |__   __|    \t")
    print("| |__ )| |    | (___| \  / |  | |       \t")
    print("| ___/ | |    \___ \| |\/| |  | |       \t")
    print("| |    | |________) | |  | |  | |       \t")
    print("|_|    \_____|_____/|_|  |_|  |_|       \t")
    print("Welcome " + ProgramName)
    print(PowerBy)
    print("My own homepage-->\n" + GithubPage)
    print(GiteePage)
    print(KsayusPage)
    print(AuthorBilibiliPage)
    print(PersonalWebsite)
    print("\nVersion:" + program_info.PCSMTVersion)
    print("-------------------------------")

def Version():
    print("-------------------------------")
    print("Version:" + program_info.PCSMTVersion)
    print("-------------------------------")