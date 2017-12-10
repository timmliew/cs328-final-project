package cs.umass.edu.myactivitiestoolkit.view.fragments;

import android.app.Fragment;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.support.annotation.NonNull;
import android.support.v4.content.LocalBroadcastManager;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.CompoundButton;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;

import java.text.FieldPosition;
import java.text.Format;
import java.text.ParsePosition;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.Locale;
import java.util.Queue;

import cs.umass.edu.myactivitiestoolkit.R;
import cs.umass.edu.myactivitiestoolkit.constants.Constants;
import cs.umass.edu.myactivitiestoolkit.services.AccelerometerService;
import cs.umass.edu.myactivitiestoolkit.services.GyroService;
import cs.umass.edu.myactivitiestoolkit.services.ServiceManager;
import cs.umass.edu.myactivitiestoolkit.services.msband.BandService;

import static android.content.Context.LAYOUT_INFLATER_SERVICE;

/**
 * Fragment which visualizes the 3-axis accelerometer signal, displays the step count estimates and
 * current activity to the user and allows the user to interact with the {@link AccelerometerService}.
 * <br><br>
 *
 * <b>ASSIGNMENT 0 (Data Collection & Visualization)</b> :
 *      In this assignment, you will display and visualize the accelerometer readings
 *      and send the data to the server. The framework is there for you; you only need
 *      to make the calls in the {@link AccelerometerService} to communicate the data.
 * <br><br>
 *
 * <b>ASSIGNMENT 1 (Step Detection)</b> :
 *      In this assignment, you will detect steps using the accelerometer sensor. You
 *      will design both a local step detection algorithm and a server-side (Python)
 *      step detection algorithm. Your algorithm should look for peaks and account for
 *      the fact that humans generally take steps every 0.5 - 2.0 seconds. Your local
 *      and server-side algorithms may be functionally identical, or you may choose
 *      to take advantage of other Python tools/libraries to improve performance.
 *  <br><br>
 *
 *  <b>ASSIGNMENT 2 (Activity Detection)</b> :
 *      In this assignment, you will classify the user's activity based on the
 *      accelerometer data. The only modification you should make to the mobile
 *      app is to register a listener which will parse the activity from the acquired
 *      {@link org.json.JSONObject} and update the UI. The real work, that is
 *      your activity detection algorithm, will be running in the Python script
 *      and acquiring data via the server.
 *
 * @author CS390MB
 *
 * @see AccelerometerService
 * @see Fragment
 */
public class ExerciseFragment extends Fragment implements AdapterView.OnItemSelectedListener {

    /** Used during debugging to identify logs by class. */
    @SuppressWarnings("unused")
    private static final String TAG = ExerciseFragment.class.getName();

    /** The switch which toggles the {@link AccelerometerService}. **/
    private Switch switchAccelerometer;

    /** The switch which toggles the {@link GyroService}. **/

    private Switch switchGyro;


    /** Displays the accelerometer x, y and z-readings. **/
    public static TextView txtAccelerometerReading;

    /** Displays the accelerometer x, y and z-readings. **/
    public static TextView txtGyroscopeReading;

    /** Displays the step count computed by the built-in Android step detector. **/
    private TextView txtAndroidStepCount;

    /** Displays the step count computed by your local step detection algorithm. **/
    private TextView txtLocalStepCount;

    /** Displays the step count computed by your server-side step detection algorithm. **/
    private TextView txtServerStepCount;

    /** Displays the activity identified by your server-side activity classification algorithm. **/
    private TextView txtActivity;

    /** The number of data points to display in the graph. **/
    private static final int GRAPH_CAPACITY = 100;

    /** The number of points displayed on the plot. This should only ever be less than
     * {@link #GRAPH_CAPACITY} before the plot is fully populated. **/
    private int mNumberOfPoints = 0;

    /**
     * The queue of timestamps.
     */
    private final Queue<Number> mTimestamps = new LinkedList<>();

    /**
     * The queue of accelerometer values along the x-axis.
     */
    private final Queue<Number> mXValues = new LinkedList<>();

    /**
     * The queue of accelerometer values along the y-axis.
     */
    private final Queue<Number> mYValues = new LinkedList<>();

    /**
     * The queue of accelerometer values along the z-axis.
     */
    private final Queue<Number> mZValues = new LinkedList<>();

    /**
     * The queue of peak timestamps.
     */
    private final Queue<Number> mPeakTimestamps = new LinkedList<>();

    /**
     * The queue of peak values.
     */
    private final Queue<Number> mPeakValues = new LinkedList<>();

    /** Reference to the service manager which communicates to the {@link AccelerometerService}. **/
    private ServiceManager mServiceManager;

    Spinner spinner;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        this.mServiceManager = ServiceManager.getInstance(getActivity());

    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        final View view = inflater.inflate(R.layout.fragment_exercise, container, false);

        //labels spinner
        spinner = (Spinner)view.findViewById(R.id.spinner_activity);
        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(getActivity(),
                R.array.labels_array, android.R.layout.simple_spinner_item);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(adapter);
        spinner.setOnItemSelectedListener(this);

        //obtain a reference to the accelerometer reading text field
        txtAccelerometerReading = (TextView) view.findViewById(R.id.txtAccelerometerReading);
        txtGyroscopeReading = (TextView) view.findViewById(R.id.txtGyroscopeReading);

        switchAccelerometer = (Switch) view.findViewById(R.id.switchAccelerometer);
        switchAccelerometer.setChecked(mServiceManager.isServiceRunning(AccelerometerService.class));
        switchAccelerometer.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean enabled) {
                if (enabled){
                    mServiceManager.startSensorService(AccelerometerService.class);
                } else {
                    Log.d(TAG, "found spinner");
                    mServiceManager.stopSensorService(AccelerometerService.class);
                }
            }
        });
        switchGyro = (Switch) view.findViewById(R.id.switchGyro);
        switchGyro.setChecked(mServiceManager.isServiceRunning(GyroService.class));
        switchGyro.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean enabled) {
                if (enabled){
                    mServiceManager.startSensorService(GyroService.class);
                } else {
                    Log.d(TAG, "found spinner");
                    mServiceManager.stopSensorService(GyroService.class);
                }
            }
        });

        return view;
    }

    @Override
    public void onStart() {
        super.onStart();


    }

    @Override
    public void onStop() {
        super.onStop();
    }

    /**
     * Displays the accelerometer reading on the UI.
     * @param x acceleration along the x-axis
     * @param y acceleration along the y-axis
     * @param z acceleration along the z-axis
     */
    private void displayAccelerometerReading(final float x, final float y, final float z){
        getActivity().runOnUiThread(new Runnable() {
            @Override
            public void run() {
                txtAccelerometerReading.setText("X: " + x);

            }
        });
    }

    public static void displayGyroscopeReading(final float x, final float y, final float z){
        txtGyroscopeReading.setText("X: " + x);
    }




    @Override
    public void onItemSelected(AdapterView<?> parent, View view,
                               int pos, long id) {
        // An item was selected. You can retrieve the selected item using
        // parent.getItemAtPosition(pos)

//        label = parent.getItemAtPosition(pos).toString();
        Log.i(TAG, "got label " + parent.getItemAtPosition(pos));



        Intent labelIntent = new Intent("LABEL");


        if (pos >= 0) {
            labelIntent.putExtra("LABEL", parent.getItemAtPosition(pos).toString());
        } else {
            labelIntent.putExtra("LABEL", "-1");
        }

        LocalBroadcastManager localBroadcastManager = LocalBroadcastManager.getInstance(getActivity());
        localBroadcastManager.sendBroadcast(labelIntent);

    }

    public void onNothingSelected(AdapterView<?> parent) {
        // Another interface callback
        Log.i(TAG, "got nothing selected");
//        label = "";
    }
}