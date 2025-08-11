from django import forms
from .models import *
from django.forms import inlineformset_factory


class MaquinaForm(forms.ModelForm):
    class Meta:
        model = Maquina
        fields = '__all__'
        exclude = ['id']  # Excluir el ID ya que es auto-generado

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        print(f"🔍 INICIALIZANDO FORM - Args: {len(args)}, Kwargs: {kwargs.keys()}")
        
        # Diccionario con placeholders para cada campo
        placeholders = {
            'nombre': 'Nombre de la máquina',
            'tipo': 'Tipo de máquina (Challenger/Defender)',
            'numero_serie': 'Número de serie',
            'equipment_number': 'Número de equipo',
            'criticality_ranking': 'Ranking de criticidad (0-5)',
            'availability': 'Disponibilidad (%)',
            'date_in_service': 'Fecha de puesta en servicio',
            'machine_age': 'Edad de la máquina (años)',
            
            # Costos de adquisición
            'purchase_price': 'Precio de compra ($)',
            'acquisition_cost': 'Costo de adquisición original ($)',
            'installation_and_training_cost': 'Costo de instalación y entrenamiento ($)',
            'setup_costs': 'Costos de configuración ($)',
            'current_resale_value': 'Valor actual de reventa ($)',
            'book_value': 'Valor en libros ($)',
            'salvage_value': 'Valor de salvamento ($)',
            
            # Costos operativos
            'annual_maintenance_labor_parts': 'Mantenimiento anual - mano de obra y piezas ($)',
            'initial_monthly_maintenance_cost': 'Costo mensual inicial de mantenimiento ($)',
            'maintenance_cost_gradient': 'Gradiente de costo de mantenimiento (%)',
            'cost_of_downtime': 'Costo de tiempo de inactividad ($/hora)',
            'operator_labor_cost': 'Costo de mano de obra del operador ($/hora)',
            'energy_consumption': 'Consumo de energía (kWh/hora)',
            'energy_cost': 'Costo de energía ($/kWh)',
            'consumable_replacement_cost_1': 'Costo de reemplazo de consumibles ($)',
            'consumable_lifespan_1': 'Vida útil del consumible (unidades producidas)',
            
            # Producción y vida útil
            'useful_life': 'Vida útil (meses)',
            'end_of_useful_life_date': 'Fecha de fin de vida útil',
            'monthly_depreciation': 'Depreciación mensual ($)',
            'production_rate': 'Tasa de producción',
            'production_rate_units': 'Unidades de tasa de producción',
            'texas_workdays': 'Días laborables por mes',
            'monthly_operating_hours': 'Horas operativas mensuales',
        }
        
        # Aplicar estilos y placeholders a todos los campos
        for field_name, field in self.fields.items():
            print(f"🔍 Configurando campo: {field_name} - Tipo: {type(field)}")
            
            field.widget.attrs['class'] = 'form-control'
            
            # Agregar placeholder si existe en el diccionario
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]
            
            # Configuraciones específicas por tipo de campo
            if isinstance(field, (forms.FloatField, forms.DecimalField, forms.IntegerField)):
                field.widget.attrs['step'] = 'any'
                # Hacer campos numéricos no requeridos para evitar errores de validación
                field.required = False
            
            # Para campos de fecha
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': placeholders.get(field_name, ''),
                })
                field.required = False
            
            # Para campos de texto
            if isinstance(field, forms.CharField):
                # Solo hacer requeridos los campos esenciales
                if field_name in ['nombre', 'tipo']:
                    field.required = True
                else:
                    field.required = False
            
            # Configuraciones específicas por campo
            if field_name in ['availability', 'maintenance_cost_gradient']:
                field.widget.attrs.update({
                    'min': '0',
                    'max': '100',
                    'step': '0.01'
                })
            
            if field_name == 'criticality_ranking':
                field.widget.attrs.update({
                    'min': '0',
                    'max': '5',
                    'step': '0.1'
                })
            
            # Para campos monetarios
            if any(keyword in field_name for keyword in ['price', 'cost', 'value', 'depreciation']):
                field.widget.attrs.update({
                    'min': '0',
                    'step': '0.01'
                })

    def clean(self):
        """Validación personalizada del formulario"""
        cleaned_data = super().clean()
        print(f"🔍 CLEANING FORM DATA: {cleaned_data}")
        
        # Validaciones básicas
        nombre = cleaned_data.get('nombre')
        tipo = cleaned_data.get('tipo')
        
        if not nombre:
            raise forms.ValidationError("El nombre de la máquina es obligatorio.")
        
        if not tipo:
            raise forms.ValidationError("El tipo de máquina es obligatorio.")
        
        # Validaciones específicas para campos numéricos
        for field_name, value in cleaned_data.items():
            if value is not None and isinstance(value, (int, float)) and value < 0:
                if any(keyword in field_name for keyword in ['price', 'cost', 'value', 'hours', 'rate']):
                    raise forms.ValidationError(f"El campo {field_name} no puede ser negativo.")
        
        return cleaned_data

    def save(self, commit=True):
        """Sobrescribir save para debugging"""
        print(f"🔍 GUARDANDO MÁQUINA - Commit: {commit}")
        
        instance = super().save(commit=False)
        print(f"🔍 INSTANCIA CREADA: {instance}")
        
        if commit:
            try:
                instance.save()
                print(f"✅ MÁQUINA GUARDADA CON ID: {instance.id}")
            except Exception as e:
                print(f"❌ ERROR AL GUARDAR INSTANCIA: {str(e)}")
                print(f"❌ TRACEBACK: {traceback.format_exc()}")
                raise
        
        return instance
    
class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ['id', 'cliente', 'fecha_entrega_cliente', 'valor_cobrar_cliente', 'observaciones']
        widgets = {
            'id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el ID del registro'
            }),
            'cliente': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_entrega_cliente': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'valor_cobrar_cliente': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que ciertos campos sean requeridos
        self.fields['id'].required = True
        self.fields['cliente'].required = True
        self.fields['fecha_entrega_cliente'].required = True
        self.fields['valor_cobrar_cliente'].required = True
        
        # Personalizar labels
        self.fields['id'].label = 'ID del Registro'
        self.fields['cliente'].label = 'Cliente'
        self.fields['fecha_entrega_cliente'].label = 'Fecha de Entrega al Cliente'
        self.fields['valor_cobrar_cliente'].label = 'Valor a Cobrar ($)'
        self.fields['observaciones'].label = 'Observaciones'

from django import forms
from django.forms import formset_factory
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Registro, Cliente, Proveedor
import json
from datetime import date

class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ['id', 'cliente', 'fecha_entrega_cliente', 'valor_cobrar_cliente', 'observaciones']
        widgets = {
            'id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el ID del registro'
            }),
            'cliente': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_entrega_cliente': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'valor_cobrar_cliente': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que ciertos campos sean requeridos
        self.fields['id'].required = True
        self.fields['cliente'].required = True
        self.fields['fecha_entrega_cliente'].required = True
        self.fields['valor_cobrar_cliente'].required = True
        
        # Personalizar labels
        self.fields['id'].label = 'ID del Registro'
        self.fields['cliente'].label = 'Cliente'
        self.fields['fecha_entrega_cliente'].label = 'Fecha de Entrega al Cliente'
        self.fields['valor_cobrar_cliente'].label = 'Valor a Cobrar ($)'
        self.fields['observaciones'].label = 'Observaciones'

# Formulario para crear/editar obligaciones individuales
class ObligacionForm(forms.Form):
    proveedor_id = forms.IntegerField(widget=forms.HiddenInput())
    proveedor_nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del proveedor'
        }),
        label='Proveedor'
    )
    valor_pagar = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00'
        }),
        label='Valor a Pagar ($)'
    )
    fecha_vencimiento = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha de Vencimiento'
    )
    descripcion = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Descripción de la obligación'
        }),
        label='Descripción'
    )
    referencia = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Referencia o número de factura'
        }),
        label='Referencia'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que ciertos campos sean requeridos
        self.fields['proveedor_nombre'].required = True
        self.fields['valor_pagar'].required = True
        self.fields['fecha_vencimiento'].required = True

# Formulario para pagos de cliente
class PagoClienteForm(forms.Form):
    monto = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00'
        }),
        label='Monto ($)'
    )
    fecha_pago = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha de Pago'
    )
    metodo_pago = forms.ChoiceField(
        choices=Registro.METODO_PAGO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Método de Pago'
    )
    referencia = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de referencia o comprobante'
        }),
        label='Referencia'
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Observaciones del pago...'
        }),
        label='Observaciones'
    )

    def __init__(self, *args, **kwargs):
        self.registro = kwargs.pop('registro', None)
        super().__init__(*args, **kwargs)
        
        # Configurar validaciones basadas en el registro
        if self.registro:
            valor_pendiente = self.registro.valor_pendiente
            if valor_pendiente > 0:
                self.fields['monto'].widget.attrs['max'] = str(valor_pendiente)
                self.fields['monto'].help_text = f'Máximo: ${valor_pendiente:,.2f}'
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if self.registro and monto:
            if monto > self.registro.valor_pendiente:
                raise ValidationError(
                    f'El monto no puede ser mayor al valor pendiente (${self.registro.valor_pendiente:,.2f})'
                )
        return monto

# Formulario para pagos a proveedores
class PagoProveedorForm(forms.Form):
    obligacion_id = forms.IntegerField(widget=forms.HiddenInput())
    monto = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00'
        }),
        label='Monto ($)'
    )
    fecha_pago = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha de Pago'
    )
    metodo_pago = forms.ChoiceField(
        choices=Registro.METODO_PAGO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Método de Pago'
    )
    referencia = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de referencia o comprobante'
        }),
        label='Referencia'
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Observaciones del pago...'
        }),
        label='Observaciones'
    )

    def __init__(self, *args, **kwargs):
        self.registro = kwargs.pop('registro', None)
        self.obligacion_id = kwargs.pop('obligacion_id', None)
        super().__init__(*args, **kwargs)
        
        # Configurar validaciones basadas en la obligación
        if self.registro and self.obligacion_id:
            valor_pendiente = self.registro.valor_pendiente_obligacion(self.obligacion_id)
            if valor_pendiente > 0:
                self.fields['monto'].widget.attrs['max'] = str(valor_pendiente)
                self.fields['monto'].help_text = f'Máximo: ${valor_pendiente:,.2f}'
            
            # Establecer el obligacion_id en el campo oculto
            self.fields['obligacion_id'].initial = self.obligacion_id
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if self.registro and self.obligacion_id and monto:
            valor_pendiente = self.registro.valor_pendiente_obligacion(self.obligacion_id)
            if monto > valor_pendiente:
                raise ValidationError(
                    f'El monto no puede ser mayor al valor pendiente (${valor_pendiente:,.2f})'
                )
        return monto

# Formulario compuesto para manejar el registro completo
class RegistroCompletoForm(forms.Form):
    """
    Formulario para manejar el registro principal junto con sus obligaciones
    """
    
    def __init__(self, *args, **kwargs):
        self.registro = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        # Si hay un registro existente, pre-cargar los datos
        if self.registro:
            self.initial.update({
                'id': self.registro.id,
                'cliente': self.registro.cliente_id,
                'fecha_entrega_cliente': self.registro.fecha_entrega_cliente,
                'valor_cobrar_cliente': self.registro.valor_cobrar_cliente,
                'observaciones': self.registro.observaciones,
            })
    
    # Campos del registro principal
    id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el ID del registro'
        }),
        label='ID del Registro'
    )
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Cliente'
    )
    fecha_entrega_cliente = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha de Entrega al Cliente'
    )
    valor_cobrar_cliente = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00'
        }),
        label='Valor a Cobrar ($)'
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones adicionales...'
        }),
        label='Observaciones'
    )
    
    # Campo JSON para las obligaciones (se manejará con JavaScript en el frontend)
    obligaciones_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    def clean_obligaciones_json(self):
        """Validar que el JSON de obligaciones sea válido"""
        obligaciones_json = self.cleaned_data.get('obligaciones_json', '[]')
        try:
            obligaciones = json.loads(obligaciones_json)
            if not isinstance(obligaciones, list):
                raise ValidationError('Las obligaciones deben ser una lista válida')
            
            # Validar cada obligación
            for i, obligacion in enumerate(obligaciones):
                if not isinstance(obligacion, dict):
                    raise ValidationError(f'La obligación {i+1} no es válida')
                
                required_fields = ['proveedor_nombre', 'valor_pagar', 'fecha_vencimiento']
                for field in required_fields:
                    if field not in obligacion or not obligacion[field]:
                        raise ValidationError(f'La obligación {i+1} debe tener {field}')
                
                # Validar que el valor sea numérico
                try:
                    valor = Decimal(str(obligacion['valor_pagar']))
                    if valor <= 0:
                        raise ValidationError(f'El valor de la obligación {i+1} debe ser mayor a 0')
                except (ValueError, TypeError):
                    raise ValidationError(f'El valor de la obligación {i+1} no es válido')
            
            return obligaciones_json
        except json.JSONDecodeError:
            raise ValidationError('El formato de las obligaciones no es válido')
    
    def save(self, commit=True):
        """Guarda el registro y sus obligaciones"""
        # Crear o actualizar el registro
        if self.registro:
            registro = self.registro
            registro.cliente_id = self.cleaned_data['cliente'].id
            registro.fecha_entrega_cliente = self.cleaned_data['fecha_entrega_cliente']
            registro.valor_cobrar_cliente = self.cleaned_data['valor_cobrar_cliente']
            registro.observaciones = self.cleaned_data['observaciones']
        else:
            registro = Registro(
                id=self.cleaned_data['id'],
                cliente=self.cleaned_data['cliente'],
                fecha_entrega_cliente=self.cleaned_data['fecha_entrega_cliente'],
                valor_cobrar_cliente=self.cleaned_data['valor_cobrar_cliente'],
                observaciones=self.cleaned_data['observaciones']
            )
        
        if commit:
            registro.save()
            
            # Procesar obligaciones si están presentes
            obligaciones_json = self.cleaned_data.get('obligaciones_json', '[]')
            if obligaciones_json:
                try:
                    obligaciones = json.loads(obligaciones_json)
                    # Limpiar obligaciones existentes
                    registro.obligaciones_data = []
                    
                    # Agregar nuevas obligaciones
                    for obligacion in obligaciones:
                        registro.agregar_obligacion(
                            proveedor_id=obligacion.get('proveedor_id', 0),
                            proveedor_nombre=obligacion['proveedor_nombre'],
                            valor_pagar=Decimal(str(obligacion['valor_pagar'])),
                            fecha_vencimiento=obligacion['fecha_vencimiento'],
                            descripcion=obligacion.get('descripcion', ''),
                            referencia=obligacion.get('referencia', '')
                        )
                except json.JSONDecodeError:
                    pass  # Ya se validó en clean_obligaciones_json
        
        return registro

# Crear formsets para uso dinámico
ObligacionFormSet = formset_factory(
    ObligacionForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
    max_num=20,
    validate_max=True
)

PagoClienteFormSet = formset_factory(
    PagoClienteForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
    max_num=50,
    validate_max=True
)

PagoProveedorFormSet = formset_factory(
    PagoProveedorForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
    max_num=50,
    validate_max=True
)
