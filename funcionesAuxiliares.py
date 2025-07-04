def transformar_nombres(anio):

    archivo_modificado = ""
    match anio:
        case 2016:
            archivo_modificado = {
                "usu_individual_t216.txt": "2016-2Trim",
                "usu_individual_t316.txt": "2016-3Trim",
                "usu_individual_t416.txt": "2016-4Trim"
            }
        case 2017:
            archivo_modificado = {
                "usu_individual_t117.txt": "2017-1Trim",
                "usu_individual_t217.txt": "2017-2Trim",
                "usu_individual_t317.txt": "2017-3Trim",
                "usu_individual_t417.txt": "2017-4Trim"
            }
        case 2018:
            archivo_modificado = {
                "usu_individual_t118.txt": "2018-1Trim",
                "usu_individual_t218.txt": "2018-2Trim",
                "usu_individual_t318.txt": "2018-3Trim",
                "usu_individual_t418.txt": "2018-4Trim"
            }
        case 2019:
            archivo_modificado = {
                "usu_individual_t119.txt": "2019-1Trim",
                "usu_individual_t219.txt": "2019-2Trim",
                "usu_individual_t319.txt": "2019-3Trim",
                "usu_individual_t419.txt": "2019-4Trim"
            }
        case 2020:
            archivo_modificado = {
                "usu_individual_t120.txt": "2020-1Trim",
                "usu_individual_t220.txt": "2020-2Trim",
                "usu_individual_t320.txt": "2020-3Trim",
                "usu_individual_t420.txt": "2020-4Trim",
            }
        case 2021:
            archivo_modificado = {
                "usu_individual_t121.txt": "2021-1Trim",
                "usu_individual_t221.txt": "2021-2Trim",
                "usu_individual_t321.txt": "2021-3Trim",
                "usu_individual_t421.txt": "2021-4Trim",
            }
        case 2022:
            archivo_modificado = {
                "usu_individual_t122.txt": "2022-1Trim",
                "usu_individual_t222.txt": "2022-2Trim",
                "usu_individual_t322.txt": "2022-3Trim",
                "usu_individual_t422.txt": "2022-4Trim",
            }
        case 2023:
            archivo_modificado = {
                "usu_individual_t123.txt": "2023-1Trim",
                "usu_individual_t223.txt": "2023-2Trim",
                "usu_individual_t323.txt": "2023-3Trim",
                "usu_individual_t423.txt": "2023-4Trim",
            }
        case 2024:
            archivo_modificado = {
                "usu_individual_t124.txt": "2024-1Trim",
                "usu_individual_t224.txt": "2024-2Trim",
                "usu_individual_t324.txt": "2024-3Trim"
            }
        case _:
            archivo_modificado = "Error. No es un año correcto"

    return archivo_modificado


def elegir_archivo(anio):
    devolver_archivo = ""
    match anio:
        case 2016:
            devolver_archivo = "periodos trimestrales/periodo 2016/individual"
        case 2017:
            devolver_archivo = "periodos trimestrales/periodo 2017/individual"
        case 2018:
            devolver_archivo = "periodos trimestrales/periodo 2018/individual"
        case 2019:
            devolver_archivo = "periodos trimestrales/periodo 2019/individual"
        case 2020:
            devolver_archivo = "periodos trimestrales/periodo 2020/individual"
        case 2021:
            devolver_archivo = "periodos trimestrales/periodo 2021/individual"
        case 2022:
            devolver_archivo = "periodos trimestrales/periodo 2022/individual"
        case 2023:
            devolver_archivo = "periodos trimestrales/periodo 2023/individual"
        case 2024:
            devolver_archivo = "periodos trimestrales/periodo 2024/individual"
        case _:
            devolver_archivo = "Error. No es un año correcto"
    
    return devolver_archivo