import re
from matplotlib import pyplot as plt ### Importa pyplot para realizar la gráfica.
from matplotlib import animation  ### Importa animation que permite actualizar la gráfica en intervalos concretos
from matplotlib import style ### Permite cambiar el estilo de nuestra gráfica.
from matplotlib.widgets import Button
import serial ### Importa librería para trabajar con el puerto serie.

style.use('fivethirtyeight')  ### cambia el estilo de nuestra gráfica.


class CurrentSerialPlot:

    def __init__(self, serialPort = '/dev/ttyACM0', serialBaud = 115200):
        self.port = serialPort
        self.baud = serialBaud
        # self.isRun = False

        ### configuracion de la figura y subplots
        self.fig = plt.figure()
        self.fig.subplots_adjust(top=0.9, bottom=0.2, right=0.9, left=0.2)
        self.ax1 = self.fig.add_subplot(1,1,1)
        ### variables para manejar plot de las lineas(datos) a mostrar
        self.showingSensor1 = True
        self.showingSensor2 = True
        self.showingSensor2 = True
        ### parámetros sobre animacion
        self.anim = None
        self.animRunning = False
        ### listas que almacenarán los datos
        self.currentSensor1 = []
        self.currentSensor2 = []
        self.currentSensor3 = []

        print(f'Trying to connect to: {str(serialPort)} at {str(serialBaud)} BAUD')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=1)
            print(f'Connected to: {str(serialPort)} at {str(serialBaud)} BAUD')
            # self.isRun = True
        except:
            print(f'Failed to connect with: {str(serialPort)} at {str(serialBaud)} BAUD')
    
    def getSerialData(self, frame):
        try:
            self.currentSensor1 = []
            self.currentSensor2 = []
            self.currentSensor3 = []
            print(f'###################### i: {frame} ######################')
            for i in range(0, 100):
                dataReaded = self.serialConnection.readline()
                print()
                print(f'data readed: {dataReaded}')
                dataDecoded = dataReaded.decode('utf-8').rstrip() ### decodifica bytes que llegan de puerto serial y elimina salto de linea
                print(f'data decoded: {dataDecoded}')
                data = dataDecoded.split(",")
                print(f'data list: {data}')
                self.saveSerialData(data)
            print(f'###################### number of dates to plot: {i} ######################')
            self.animate()
        except UnicodeDecodeError as ude:
            print('UnicodeDecodeError0:', ude)
            pass
    
    def saveSerialData(self, data):
        floatRegex = r'^-?\d+(?:\.\d+)?$' ### regex para validar que el dato sea float
        try:
            ### if/else para validar que serial envíe lista de 3 datos
            ### if/else dentro para validar que el dato (contra regex ) sea float
            if 0 < len(data):
                if re.match(floatRegex, data[0]):
                    self.currentSensor1.append(data[0])
                else:
                    self.currentSensor1.append(self.currentSensor1[-1])
            else:
                self.currentSensor1.append(self.currentSensor1[-1])

            if 1 < len(data):
                if re.match(floatRegex, data[1]):
                    self.currentSensor2.append(data[1])
                else:
                    self.currentSensor2.append(self.currentSensor2[-1])
            else:
                self.currentSensor2.append(self.currentSensor2[-1])

            if 2 < len(data):
                if re.match(floatRegex, data[2]):
                    self.currentSensor3.append(data[2])
                else:
                    self.currentSensor3.append(self.currentSensor3[-1])
            else:
                self.currentSensor3.append(self.currentSensor3[-1])
        except IndexError as ie:
            print("IndexError1:", ie)
            pass
        except UnicodeDecodeError as ude:
            print("UnicodeDecodeError1:", ude)
            pass
        # except Exception as e:
        #     print("exception1:", e)
        #     self.currentSensor1.append(str(0))
        #     self.currentSensor2.append(str(0))
        #     self.currentSensor3.append(str(0))
        #     pass
        finally:
            print(f'{self.currentSensor1[-1]} - {self.currentSensor2[-1]} - {self.currentSensor3[-1]}')
    
    def animate(self):
        self.ax1.clear() ### Limpia la gráfica para volver a pintar.
        self.ax1.set_ylim([0,500]) ### Ajusta el límite vertical de la gráfica.
        self.ax1.set_ylabel('Power (W)') ### nombre del eje y
        self.ax1.set_xlabel('time (ms)') ### nombre del eje x
        self.ax1.set_title('Power consumption') ### titulo de la grafica
        try:  ### Permite comprobar si hay un error al ejecutar la siguiente instrucción.
            if self.showingSensor1: ### verifica si se muestra o no linea para sensor1
                self.ax1.plot(range(0,100), self.currentSensor1, color='#F44336') # Plotea los datos en x de 0 a 100.
            self.ax1.plot(range(0,100), self.currentSensor2, color='#1565C0') # Plotea los datos en x de 0 a 100.
            self.ax1.plot(range(0,100), self.currentSensor3, color='#FFC107') # Plotea los datos en x de 0 a 100.
            self.ax1.legend(['sensor1', 'sensor2', 'sensor3'], loc='upper left') ### legends de cada linea (plot)
        except UnicodeDecodeError as ude: ### Si se produce el error al plotear no hace nada y evita que el programa se pare.
            print("UnicodeDecodeError2:", ude)
            pass
        except ValueError as ve:
            print("ValueError2:", ve)
            pass

    def start(self):
        self.anim = animation.FuncAnimation(self.fig, self.getSerialData, interval=100) ### Crea animacion para que se ejecute la función, plotea con un intervalo de 100ms.
        axSensor1 = plt.axes([0.81, 0.05, 0.08, 0.075]) ### ajustes graficos sensor1
        sensor1Button = Button(axSensor1, 'Sensor1') 
        sensor1Button.on_clicked(self._showSensor1) ### callback boton sensor1
        # axSensor2 = plt.axes([0.71, 0.05, 0.08, 0.075])
        # sensor2 = Button(axSensor2, 'Sensor2')
        axPause = plt.axes([0.71, 0.05, 0.08, 0.075]) ### ajustes graficos boton pausa
        pauseButton = Button(axPause, 'Pause') 
        pauseButton.on_clicked(self._pause) ### callback boton pausa
        plt.show() ### Muestra la gráfica.

    def _showSensor1(self, event):
        print(self.showingSensor1)
        if self.showingSensor1:
            self.showingSensor1 = False
        else:
            self.showingSensor1 = True
        print(self.showingSensor1)

    def _pause(self, event):
        if self.animRunning:
            self.anim.event_source.stop()
            self.animRunning = False
        else:
            self.anim.event_source.start()
            self.animRunning = True

    def close(self):
        # self.isRun = False
        # self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')

if __name__ == "__main__":
    try:
        portName = '/dev/ttyACM0'
        baudRate = 115200
        s = CurrentSerialPlot(portName, baudRate)
        s.start()

        s.close()
    except KeyboardInterrupt:
        s.close()
    except Exception as e:
        print(f'main error: {e}')
        s.close()
