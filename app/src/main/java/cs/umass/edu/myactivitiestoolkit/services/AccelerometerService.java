package cs.umass.edu.myactivitiestoolkit.services;

import android.app.FragmentContainer;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.support.v4.content.LocalBroadcastManager;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.os.Bundle;
import android.widget.Spinner;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import cs.umass.edu.myactivitiestoolkit.R;
import cs.umass.edu.myactivitiestoolkit.constants.Constants;
import cs.umass.edu.myactivitiestoolkit.steps.StepDetector;
import cs.umass.edu.myactivitiestoolkit.view.activities.MainActivity;
import cs.umass.edu.myactivitiestoolkit.view.fragments.ExerciseFragment;
import edu.umass.cs.MHLClient.client.MessageReceiver;
import edu.umass.cs.MHLClient.client.MobileIOClient;
import edu.umass.cs.MHLClient.sensors.AccelerometerReading;
import edu.umass.cs.MHLClient.sensors.GyroscopeReading;
import edu.umass.cs.MHLClient.sensors.SensorReading;


public class AccelerometerService extends SensorService implements SensorEventListener {

    /** Sensor Manager object for registering and unregistering system sensors */
    private SensorManager mSensorManager;


    /** Manages the physical accelerometer sensor on the phone. */
    private Sensor mAccelerometerSensor;

    /** The spinner containing the activity label. */
    Spinner spinner;

    /** The activity label for data collection. */
    String label = "";

    public void onCreate(Bundle savedInstanceState)
    {
        //get a hook to the sensor service
        mSensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);
//        mGyroscopeSensor = mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
    }


    @Override
    protected void onServiceStarted() {
        registerSensors();

        Log.i(TAG, "registered spinner listener");

        BroadcastReceiver receiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                if (intent.getAction().equals("LABEL")) {
                    label = intent.getStringExtra("LABEL");
                }
            }
        };

        LocalBroadcastManager localBroadcastManager = LocalBroadcastManager.getInstance(this);
        localBroadcastManager.registerReceiver(receiver, new IntentFilter("LABEL"));
    }

    @Override
    protected void onServiceStopped() {
        unregisterSensors();


    }

    @Override
    public void onConnected() {
        super.onConnected();
        mClient.registerMessageReceiver(new MessageReceiver(Constants.MHLClientFilter.STEP_DETECTED) {
            @Override
            protected void onMessageReceived(JSONObject json) {
                Log.d(TAG, "Received step update from server.");
                try {
                    JSONObject data = json.getJSONObject("data");
                    long timestamp = data.getLong("timestamp");
                    Log.d(TAG, "Step occurred at " + timestamp + ".");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        });
        mClient.registerMessageReceiver(new MessageReceiver(Constants.MHLClientFilter.ACTIVITY_DETECTED) {
            @Override
            protected void onMessageReceived(JSONObject json) {
                String activity;
                try {
                    JSONObject data = json.getJSONObject("data");
                    activity = data.getString("activity");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        });
    }

    /**
     * Register accelerometer sensor listener
     */
    @Override
    protected void registerSensors(){

        mSensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);
        mAccelerometerSensor = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        mSensorManager.registerListener(this, mAccelerometerSensor, SensorManager.SENSOR_DELAY_NORMAL);

//        mGyroscopeSensor = mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
//        mSensorManager.registerListener(this, mGyroscopeSensor, SensorManager.SENSOR_DELAY_NORMAL);

        //TODO : (Assignment 0) Register the accelerometer sensor from the sensor manager.
    }

    /**
     * Unregister the sensor listener, this is essential for the battery life!
     */
    @Override
    protected void unregisterSensors() {
        //TODO : Unregister your sensors. Make sure mSensorManager is not null before calling its unregisterListener method.
        if (mSensorManager == null)
            mSensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);

        if (mAccelerometerSensor == null)
            mAccelerometerSensor = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);

        mSensorManager.unregisterListener(this, mAccelerometerSensor);
    }

    @Override
    protected int getNotificationID() {
        return Constants.NOTIFICATION_ID.ACCELEROMETER_SERVICE;
    }

    @Override
    protected String getNotificationContentText() {
        return getString(R.string.activity_service_notification);
    }

    @Override
    protected int getNotificationIconResourceID() {
        return R.drawable.ic_running_white_24dp;
    }


    @Override
    public void onSensorChanged(SensorEvent event) {

        if(event.sensor.getType() == Sensor.TYPE_ACCELEROMETER){
            ExerciseFragment.txtAccelerometerReading.setText(" X: " + event.values[0]
                    + " Y: " + event.values[1] + " Z: " + event.values[2]);

            // convert the timestamp to milliseconds (note this is not in Unix time)
            long timestamp_in_milliseconds = (long) ((double) event.timestamp / Constants.TIMESTAMPS.NANOSECONDS_PER_MILLISECOND);

            int labelInt = -1;
            if (!(label.equals("") || label.equals("Label"))) {
                labelInt = Integer.parseInt("" + label.charAt(0));
            }

            mClient.sendSensorReading(new AccelerometerReading(getString(R.string.mobile_health_client_user_id), "MOBILE", "", timestamp_in_milliseconds,labelInt, event.values));

        }

    }

        @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        Log.i(TAG, "Accuracy changed: " + accuracy);
    }

}