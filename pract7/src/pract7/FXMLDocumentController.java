/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package pract7;

import java.net.URL;
import java.sql.Date;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.time.LocalDate;
import java.util.Calendar;
import java.util.ResourceBundle;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.concurrent.Task;
import java.time.LocalTime;
import javafx.application.Platform;
import javafx.beans.binding.Bindings;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.concurrent.Service;

/**
 *
 * @author alcargra
 */
public class FXMLDocumentController implements Initializable {
    
    @FXML
    private Label hora;
    @FXML
    private Button mostrar;
    @FXML
    private Button parar;
    
    Hora h;
    

    
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        
    }    

    @FXML
    private void mostrarHora(ActionEvent event) {
        String texto;
        h = new Hora();
        h.start();
        
    }

    @FXML
    private void pararHora(ActionEvent event) {
        h.cancel();
    }
    
    
    class Tarea extends Task<String>{
        public Tarea(){}
        @Override
        protected String call() throws Exception{
            String res = "";
            while(true){
                res = LocalTime.now().toString().substring(0,8);
                updateValue(res);
                Platform.runLater(()->{
                    hora.textProperty().bind(Bindings.convert(h.valueProperty()));
                });
                try{
                    Thread.sleep(1000);
                }catch(Exception e){if(isCancelled()) break;}
            }
            
            return res;
            
        }
    }
    
    class Hora extends Service<String>{
        public Hora(){}
        @Override
        protected Task<String> createTask(){
            return new Tarea();
            
        }
    }
    
}
