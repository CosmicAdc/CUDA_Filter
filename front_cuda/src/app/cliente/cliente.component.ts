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
    ruta_imagenes_back='http://localhost:8000/'
    finalImageUrl: string | undefined = '/assets/no_image.png';
    tiempo_tot: number = 0; 
    bloques_lanzados: number = 0; 
    grids_lanzados: number = 0; 
    ancho: number = 0; 
    alto: number = 0; 
    filtro_usado:  string | null = null; 


    imageUrl: string | ArrayBuffer | null = null;
    selectedFilter: string | null = null;
    imageName: string | null = null; 
    maskSize: number = 5; 
    blockX: number = 16;
    blockY: number = 16;
    

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
              return this.clienteService.filtroMediana(params);
            } else if(this.selectedFilter=='Gauss'){
              return this.clienteService.filtroGauss(params);
            } else {
              return of(null);
            }
          })
        ).subscribe(
          response2 => {
            var pre_ruta = response2.ruta_imagen;
            this.finalImageUrl = this.ruta_imagenes_back+pre_ruta.substring(4);
            this.tiempo_tot = response2.tiempo
            this.filtro_usado= response2.filtro
            this.ancho= response2.ancho
            this.alto = response2.alto
            this.bloques_lanzados=response2.bloques
            this.grids_lanzados=response2.grids
            console.log('Segundo servicio completado:', response2, this.finalImageUrl);

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