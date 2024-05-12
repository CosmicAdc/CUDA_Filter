import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ClienteService {

  constructor(private http: HttpClient) { }

  ruta="http://localhost:8000/"

  uploadImage(image: string | ArrayBuffer, filter: string, filename: string) {
    const blob = this.base64toBlob(image);
    const file = new File([blob], filename); // Utiliza el nombre de archivo proporcionado

    const formData = new FormData();
    formData.append('files', file);

    return this.http.post<any>(this.ruta + 'upload/', formData);
  }

  base64toBlob(base64Data: string | ArrayBuffer): Blob {
    const byteString = atob(base64Data.toString().split(',')[1]);
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: 'image/jpeg' });
  }

  filtroSobel(params: any): Observable<any> {
    return this.http.post<any>(this.ruta + 'filtroSobel/', params);
  }
  filtroMediana(params: any): Observable<any> {
    return this.http.post<any>(this.ruta + 'Mediana/', params);
  }

  filtroGauss(params: any): Observable<any> {
    return this.http.post<any>(this.ruta + 'Gauss/', params);
  }




}
