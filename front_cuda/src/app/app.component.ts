import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ClienteComponent } from './cliente/cliente.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet,ClienteComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'front_cuda';
}
