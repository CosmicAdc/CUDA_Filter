  import { CommonModule } from '@angular/common';
  import { Component } from '@angular/core';
  import { ClienteService } from '../services/cliente.service';
  import { HttpClientModule } from '@angular/common/http';
  import { FormsModule } from '@angular/forms';
  import { switchMap } from 'rxjs';
  import { of } from 'rxjs';

  @Component({
    selector: 'app-cliente',
    standalone: true,
    imports: [CommonModule,HttpClientModule,FormsModule],
    templateUrl: './cliente.component.html',
    styleUrl: './cliente.component.scss'
  })

  export class ClienteComponent {

    constructor(private clienteService: ClienteService) { } 


    imageUrl: string | ArrayBuffer | null = null;
    selectedFilter: string | null = null;
    imageName: string | null = null; 
    maskSize: number = 5; 
    blockX: number = 8;
    blockY: number = 8;

    applyFilter(filter: string) {
      this.selectedFilter = filter;
    }


    onFileSelected(event: any) {
      const file: File = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = (e: any) => {
          this.imageUrl = e.target.result;
          this.imageName = file.name; 
        };
      }
    }

    applySelectedFilter() {
      if (this.selectedFilter && this.imageUrl && this.imageName && this.maskSize && this.blockX && this.blockY) {

        const params = {
          mascara: this.maskSize,
          bloques_x: this.blockX,
          bloques_y: this.blockY,
          path_file: this.imageName 
        };


        this.clienteService.uploadImage(this.imageUrl, this.selectedFilter, this.imageName).pipe(
          switchMap((response1) => {
            console.log('Imagen enviada exitosamente:', response1);
            if (this.selectedFilter=='SobelX'){
              return this.clienteService.filtroSobel(params);
            } else if (this.selectedFilter=='Mediana') {
              return this.clienteService.filtroSobel(params);
            } else if(this.selectedFilter=='Gauss'){
              return this.clienteService.filtroSobel(params);
            } else {
              return of(null);
            }
          })
        ).subscribe(
          response2 => {
            console.log('Segundo servicio completado:', response2);
          },
          error => {
            console.error('Error en el segundo servicio:', error);
          }
        );
      } else {
        console.log('Faltan datos necesarios para aplicar el filtro.');
      }
    }

    
    validateMaskSize(event: any) {
      let value = parseInt(event.target.value);
      if (value % 2 === 0) {
        event.target.value = (value - 1).toString();
        this.maskSize = value - 1; 
      }
    }

  }