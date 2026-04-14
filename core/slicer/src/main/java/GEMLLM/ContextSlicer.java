package ir.ac.ilam.tanhaei;

import com.fasterxml.jackson.databind.ObjectMapper;
import soot.PackManager;
import soot.Scene;
import soot.SootMethod;
import soot.options.Options;
import soot.jimple.toolkits.callgraph.CallGraph;
import soot.jimple.toolkits.callgraph.Edge;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

public class ContextSlicer {
    public void buildWPCG(String classpath, String mainClass) {
        soot.G.reset();
        Options.v().set_prepend_classpath(true);
        Options.v().set_soot_classpath(classpath);
        Options.v().set_process_dir(Collections.singletonList(classpath));
        Options.v().set_whole_program(true);
        Options.v().set_allow_phantom_refs(true);
        Options.v().set_no_bodies_for_excluded(true);
        Options.v().set_output_format(Options.output_format_none);
        Options.v().setPhaseOption("cg.spark", "on");
        if (mainClass != null && !mainClass.isEmpty()) {
            Options.v().set_main_class(mainClass);
        }
        Scene.v().loadNecessaryClasses();
        PackManager.v().runPacks();
    }

    public Map<String, Object> extractContext(String targetMethodSig) {
        CallGraph cg = Scene.v().getCallGraph();
        SootMethod targetMethod = Scene.v().getMethod(targetMethodSig);

        List<String> callers = new ArrayList<>();
        Iterator<Edge> edges = cg.edgesInto(targetMethod);
        while (edges.hasNext()) {
            Edge e = edges.next();
            callers.add(e.getSrc().method().getSignature());
        }

        Map<String, Object> slice = new HashMap<>();
        slice.put("mutated_method", targetMethodSig);
        slice.put("callers", callers);
        slice.put("guards", "");
        slice.put("data_flow", "");
        return slice;
    }

    public void writeSlice(String outputPath, Map<String, Object> slice) throws IOException {
        File out = new File(outputPath);
        File parent = out.getParentFile();
        if (parent != null) {
            parent.mkdirs();
        }
        ObjectMapper mapper = new ObjectMapper();
        mapper.writerWithDefaultPrettyPrinter().writeValue(out, slice);
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("Usage: ContextSlicer <classpath-dir> <main-class> <output-json> [target-method-signature]");
            System.exit(1);
        }

        String classpath = args[0];
        String mainClass = args[1];
        String outputPath = args[2];
        String targetMethodSig = args.length >= 4 && !args[3].isEmpty()
                ? args[3]
                : "<" + mainClass + ": void main(java.lang.String[])>";

        ContextSlicer slicer = new ContextSlicer();
        slicer.buildWPCG(classpath, mainClass);
        Map<String, Object> slice = slicer.extractContext(targetMethodSig);
        slicer.writeSlice(outputPath, slice);
        System.out.println("Wrote slice to " + outputPath);
    }
}
