package cs.umass.edu.myactivitiestoolkit.services;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.util.Log;
import android.widget.Spinner;

import org.json.JSONException;
import org.json.JSONObject;

import cs.umass.edu.myactivitiestoolkit.R;
import cs.umass.edu.myactivitiestoolkit.constants.Constants;
import cs.umass.edu.myactivitiestoolkit.view.fragments.ExerciseFragment;
import edu.umass.cs.MHLClient.client.MessageReceiver;
import edu.umass.cs.MHLClient.client.MobileIOClient;
import edu.umass.cs.MHLClient.sensors.AccelerometerReading;
import edu.umass.cs.MHLClient.sensors.GyroscopeReading;
import edu.umass.cs.MHLClient.sensors.SensorReading;

/**
 * Created by liew_timothy on 12/9/17.
 */

public class GyroService  extends SensorService implements SensorEventListener {

    /** Sensor Manager object for registering and unregistering system sensors */
    private SensorManager mSensorManager;


    private Sensor mGyroscopeSensor;

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
        mGyroscopeSensor = mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        mSensorManager.registerListener(this, mGyroscopeSensor, SensorManager.SENSOR_DELAY_NORMAL);
    }

    /**
     * Unregister the sensor listener, this is essential for the battery life!
     */
    @Override
    protected void unregisterSensors() {
        if (mSensorManager == null)
            mSensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);

        if (mGyroscopeSensor == null)
            mGyroscopeSensor = mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);

        mSensorManager.unregisterListener(this, mGyroscopeSensor);

    }

    @Override
    protected int getNotificationID() {
        return Constants.NOTIFICATION_ID.GYROSCOPE_SERVICE;
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
        if(event.sensor.getType() == Sensor.TYPE_GYROSCOPE) {
            ExerciseFragment.txtGyroscopeReading.setText(" X: " + Float.toString(event.values[0])
                    + " Y: " + Float.toString(event.values[1]) + " Z: " + Float.toString(event.values[2]));

            // convert the timestamp to milliseconds (note this is not in Unix time)
            long timestamp_in_milliseconds = (long) ((double) event.timestamp / Constants.TIMESTAMPS.NANOSECONDS_PER_MILLISECOND);

            int labelInt = -1;
            if (!(label.equals("") || label.equals("Label"))) {
                labelInt = Integer.parseInt("" + label.charAt(0));
            }

            mClient.sendSensorReading(new GyroscopeReading(getString(R.string.mobile_health_client_user_id), "MOBILE", "", timestamp_in_milliseconds, labelInt, event.values));
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        Log.i(TAG, "Accuracy changed: " + accuracy);
    }

}