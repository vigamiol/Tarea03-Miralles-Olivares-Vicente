
import requests
import sys
import getopt
import time
import subprocess

global computadorIP
computadorIP = "192.168.1.30"

def obtener_datos_por_ip(ip):
    #"aplica la mascara" a la direcicon ip del computador
    aux=computadorIP.split('.')
    compa='.'.join(aux[:3])
    #"aplica la mascara" a la direccion ip que se quiere buscar para comprobar si pertenecen a la misma red
    prueba=ip.split('.')
    comprobacion='.'.join(prueba[:3])
    if compa==comprobacion:
        try:
            # Ejecutar el comando ARP para obtener la dirección MAC
            resultado = subprocess.check_output(["arp", "-a", ip])
            # Decodificar la salida en una cadena
            resultado = resultado.decode("ISO-8859-1")
            # Buscar la dirección MAC en la salida
            partes = resultado.split()
            mac = partes[11] 
              
            return mac
        except Exception as e:
            print("Error al obtener la dirección MAC:", str(e))
    else:
        print("Error: ip is outside the host network")
        sys.exit(2)
    return None


def datos_mac(mac_address):
    try:
        url = f'https://api.maclookup.app/v2/macs/{mac_address}'

        start_time = time.time()

        response = requests.get(url)

        end_time = time.time()
        response_time = end_time - start_time
        
    
        print(f'Status Code: {response.status_code}')

        if response.status_code == 200:
            if response.json()['found'] == True:
                empresa = response.json()['company']
                print(f'MAC address: {mac_address}')
                print('Fabricante:', empresa)
                print(f'Tiempo de respuesta: {response_time:.4f} segundos')
            else:
                print(f'MAC address: {mac_address}')
                print('Fabricante: no existe')
                print(f'Tiempo de respuesta: {response_time:.4f} segundos')
    except Exception as e:
        print(f'Error: {e}')

def tabla_arp():
    try:
        arp_output = subprocess.getoutput("arp -a").split('\n')[3:]
        arp_entries = [line.split() for line in arp_output if line.strip()]

        print("IP/MAC/Fabricante:")
        for entry in arp_entries:
            ip = entry[0]
            mac = entry[1]

            try:
                url = f'https://api.maclookup.app/v2/macs/{mac}'
                response = requests.get(url)

                if response.status_code == 200 and response.json()['found'] == True:
                    response_json = response.json()
                    fabricante = response_json['company']
                else:
                    fabricante = "Not found"
            except Exception as e:
                fabricante = str(e)

            print(f"{ip} / {mac} / {fabricante}")
    except Exception as e:
        print(f"Error: {e}")

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "", ["mac=", "ip=", "arp", "help"])
    except getopt.GetoptError:
        print("Use: python OUILookup.py --mac <MAC> | --ip <IP> | --arp | --help \n --mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.  \n --ip: IP del host a consultar. \n --arp: muestra los fabricantes de los host disponibles en la tabla arp. \n --help: muestra este mensaje y termina.")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("--mac"):
            datos_mac(arg)
            sys.exit()
        elif opt in ("--ip"):
            resultado=obtener_datos_por_ip(arg)
            datos_mac(resultado)
            sys.exit()
        elif opt in ("--help"):
            print("Use: python OUILookup.py --mac <MAC> | --ip <IP> | --arp | --help \n --mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.  \n --ip: IP del host a consultar. \n --arp: muestra los fabricantes de los host disponibles en la tabla arp. \n --help: muestra este mensaje y termina.")
            sys.exit()
        elif opt in ("--arp"):
            tabla_arp()
            sys.exit()

    print("Use: python OUILookup.py --ip <IP> | --mac <IP> | --arp | [--help] \n --ip : IP del host a consultar. \n --mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.  \n --arp: muestra los fabricantes de los host disponibles en la tabla arp. \n --help: muestra este mensaje y termina.")
    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])