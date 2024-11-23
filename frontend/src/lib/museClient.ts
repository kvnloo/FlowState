export class MuseClient {
  private device: BluetoothDevice | null = null;
  private server: BluetoothRemoteGATTServer | null = null;
  private eegCharacteristics: BluetoothRemoteGATTCharacteristic[] = [];

  async connect() {
    try {
      this.device = await navigator.bluetooth.requestDevice({
        filters: [{ namePrefix: 'Muse' }],
        optionalServices: ['0000fe8d-0000-1000-8000-00805f9b34fb']
      });

      this.server = await this.device.gatt?.connect();
      const service = await this.server?.getPrimaryService('0000fe8d-0000-1000-8000-00805f9b34fb');
      
      // Get EEG characteristics for all channels
      const characteristics = await service?.getCharacteristics();
      this.eegCharacteristics = characteristics?.filter(char => 
        char.uuid.startsWith('273e000')) || [];

      return true;
    } catch (error) {
      console.error('Connection failed:', error);
      return false;
    }
  }

  async startMonitoring(callback: (data: number[]) => void) {
    for (const characteristic of this.eegCharacteristics) {
      await characteristic.startNotifications();
      characteristic.addEventListener('characteristicvaluechanged', 
        (event: Event) => {
          const value = (event.target as BluetoothRemoteGATTCharacteristic).value;
          if (value) {
            const data = new Float32Array(value.buffer);
            callback(Array.from(data));
          }
        }
      );
    }
  }

  async disconnect() {
    if (this.device?.gatt?.connected) {
      await this.device.gatt.disconnect();
    }
  }
}