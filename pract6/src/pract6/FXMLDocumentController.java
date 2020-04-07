/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package pract6;

import java.net.URL;
import java.util.ResourceBundle;
import javafx.collections.*;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.geometry.Pos;
import javafx.scene.chart.*;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.image.ImageView;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.Pane;
import javafx.scene.layout.StackPane;

/**
 *
 * @author Vicent
 */
public class FXMLDocumentController implements Initializable {
    
    private Label label;
    @FXML
    private Button suspenso;
    @FXML
    private Button aprobado;
    @FXML
    private Button bien;
    @FXML
    private Button notable;
    @FXML
    private Button sobresaliente;
    @FXML
    private Button barras;
    @FXML
    private Button lineas;
    @FXML
    private Button modoOscuro;
    @FXML
    private PieChart graftarta;
    @FXML
    private BarChart<?, ?> grafbarras;
    @FXML
    private LineChart<String, Number> graflineas;
    private ObservableList<PieChart.Data> graftartaData;
    private ObservableList<XYChart.Data <String, Number>> graflineasData;
     private ObservableList<XYChart.Data <String, Number>> grafbarrasData;
    private XYChart.Series serie;
    private XYChart.Series seriebarra;
    @FXML
    private CategoryAxis xAxis;
    @FXML
    private NumberAxis yAxis;
    @FXML
    private NumberAxis yAxisB;
    @FXML
    private CategoryAxis xAxisB;
    private int estilo = 0;
    @FXML
    private AnchorPane ventana;
    @FXML
    private Label titulo;
    @FXML
    private StackPane stack;
    
    
    private void handleButtonAction(ActionEvent event) {
        System.out.println("You clicked me!");
        label.setText("Hello World!");
    }
    
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // TODO
        ventana.getStyleClass().add("ventana");
        titulo.getStyleClass().add("titulo");
        
        graftartaData = FXCollections.observableArrayList(
        new PieChart.Data("Suspenso", 0),
        new PieChart.Data("Aprobado",0),
        new PieChart.Data("Bien", 0),
        new PieChart.Data("Notable", 0),
        new PieChart.Data("Sobresaliente", 0)
        );
        graftarta.setData(graftartaData);
       
        xAxis = new CategoryAxis();
        yAxis = new NumberAxis();
        graflineasData = FXCollections.observableArrayList();
        serie = new XYChart.Series(graflineasData);
        serie.getData().add(new XYChart.Data("Suspenso", 0));
        serie.getData().add(new XYChart.Data("Aprobado", 0));
        serie.getData().add(new XYChart.Data("Bien", 0));
        serie.getData().add(new XYChart.Data("Notable", 0));
        serie.getData().add(new XYChart.Data("Sobresaliente", 0));
        serie.setName("Alumnos por cada nota");
        graflineas.getData().addAll(serie);
    
        xAxisB = new CategoryAxis();
        yAxisB = new NumberAxis();
        grafbarrasData = FXCollections.observableArrayList();
        seriebarra = new XYChart.Series(grafbarrasData);
        seriebarra.setName("Alumnos por cada nota");
        seriebarra.getData().add(new XYChart.Data("Suspenso",0));
        seriebarra.getData().add(new XYChart.Data("Aprobado",0));
        seriebarra.getData().add(new XYChart.Data("Bien",0));
        seriebarra.getData().add(new XYChart.Data("Notable",0));
        seriebarra.getData().add(new XYChart.Data("Sobresaliente",0));
        grafbarras.getData().add(seriebarra);
    } 
    

    @FXML
    private void addaprobado(ActionEvent event) {
        for (PieChart.Data item : graftartaData) {
            String name = item.getName();
            if(name.equals("Aprobado")){
            int valorActual = (int) item.getPieValue() ; 
            item.setPieValue(valorActual + 1);break;}
           }
        
        for (XYChart.Data<String, Number> item : graflineasData ){ 
            String x = item.getXValue(); 
            if(x.equals("Aprobado")){
            int valorActual = item.getYValue().intValue() ; 
            item.setYValue(valorActual + 1);break;}}
        
        for (XYChart.Data<String, Number> item : grafbarrasData ){ 
            String x = item.getXValue(); 
            if(x.equals("Aprobado")){
            int valorActual = item.getYValue().intValue() ; 
            item.setYValue(valorActual + 1);break;}}
    }

    @FXML
    private void addbien(ActionEvent event) {
         for (PieChart.Data item : graftartaData) {
            String name = item.getName();
            if(name.equals("Bien")){
            int valorActual = (int) item.getPieValue() ; 
            item.setPieValue(valorActual + 1);break;}
            }
         
         for (XYChart.Data<String, Number> item : graflineasData ){ 
            String x = item.getXValue(); 
            if(x.equals("Bien")){
            int valorActual = item.getYValue().intValue() ; 
            item.setYValue(valorActual + 1);break;}}
        
        for (XYChart.Data<String, Number> item : grafbarrasData ){ 
            String x = item.getXValue(); 
            if(x.equals("Bien")){
            int valorActual = item.getYValue().intValue() ; 
            item.setYValue(valorActual + 1);break;}}
    }

    @FXML
    private void addnotable(ActionEvent event) {
         for (PieChart.Data item : graftartaData) {
            String name = item.getName();
            if(name.equals("Notable")){
            int valorActual = (int) item.getPieValue() ; 
            item.setPieValue(valorActual + 1);break;}
            }
         
         for (XYChart.Data<String, Number> item : graflineasData ){ 
            String x = item.getXValue(); 
            if(x.equals("Notable")){
            int valorActual = item.getYValue().intValue() ; 
            item.setYValue(valorActual + 1);break;}}
        
        for (XYChart.Data<String, Number> item : grafbarrasData ){ 
            String x = item.getXValue(); 
            if(x.equals("Notable")){
            int valorActual = item.getYValue().intValue() ; 
            item.setYValue(valorActual + 1);break;}}
    }

    @FXML
    private void addsobresaliente(ActionEvent event) {
         for (PieChart.Data item : graftartaData) {
            String name = item.getName();
            if(name.equals("Sobresaliente")){
            int valorActual = (int) item.getPieValue() ; 
            item.setPieValue(valorActual + 1);break;}
            }
         
         for (XYChart.Data<String, Number> item : graflineasData ){ 
            String x = item.getXValue(); 
            if(x.equals("Sobresaliente")){
            int valorActual = item.getYValue().intValue() ; 
            item.setYValue(valorActual + 1);break;}}
        
        for (XYChart.Data<String, Number> item : grafbarrasData ){ 
            String x = item.getXValue(); 
            if(x.equals("Sobresaliente")){
            int valorActual = item.getYValue().intValue() ; 
            item.setYValue(valorActual + 1);break;}}
    }

    @FXML
    private void addsuspenso(ActionEvent event) {
         for (PieChart.Data item : graftartaData) {
            String name = item.getName();
            if(name.equals("Suspenso")){
            int valorActual = (int) item.getPieValue() ; 
            item.setPieValue(valorActual + 1);break;}
            }
         
         for (XYChart.Data<String, Number> item : graflineasData ){ 
            String x = item.getXValue(); 
            if(x.equals("Suspenso")){
            int valorActual = item.getYValue().intValue() ; 
            item.setYValue(valorActual + 1);break;}}
        
        for (XYChart.Data<String, Number> item : grafbarrasData ){ 
            String x = item.getXValue(); 
            if(x.equals("Suspenso")){
            int valorActual = item.getYValue().intValue() ; 
            item.setYValue(valorActual + 1);break;}}
    }

    @FXML
    private void mostrarbarras(MouseEvent event) {
        grafbarras.setVisible(true);
    }

    @FXML
    private void mostrarlineas(MouseEvent event) {
        grafbarras.setVisible(false);
    }

    @FXML
    private void cambiarmodo(MouseEvent event) {
        String css;
        estilo++;
        if(estilo%2==1){css = this.getClass().getResource("modooscuro.css").toExternalForm();}
        else{css = this.getClass().getResource("estilos.css").toExternalForm();}
        ventana.getStylesheets().remove(css);
        ventana.getStylesheets().add(css);
    }

}