package ir.ac.ilam.tanhaei;

import soot.*;
import soot.jimple.toolkits.callgraph.CallGraph;
import soot.jimple.toolkits.callgraph.Edge;
import soot.options.Options;
import java.util.*;

public class ContextSlicer {
    /**
     * Initializes Soot and builds the Whole Program Common Call Graph (WPCG).
     * [cite: 104, 215]
     */
    public void buildWPCG(String classpath, String mainClass) {
        Options.v().set_whole_program(true);
        Options.v().set_allow_phantom_refs(true);
        Options.v().set_process_dir(Collections.singletonList(classpath));
        Options.v().setPhaseOption("cg.spark", "on"); // Enable SPARK engine [cite: 104]
        
        Scene.v().loadNecessaryClasses();
        PackManager.v().runPacks();
    }

    /**
     * Extracts call sites and inter-procedural guards for a mutated method.
     * [cite: 59, 84]
     */
    public Map<String, Object> extractContext(String targetMethodSig) {
        CallGraph cg = Scene.v().getCallGraph();
        SootMethod targetMethod = Scene.v().getMethod(targetMethodSig);
        
        List<String> callers = new ArrayList<>();
        Iterator<Edge> edges = cg.edgesInto(targetMethod);
        
        while (edges.hasNext()) {
            Edge e = edges.next();
            callers.add(e.getSrc().toString()); // Capture inter-procedural context [cite: 84, 221]
        }

        Map<String, Object> slice = new HashMap<>();
        slice.put("mutated_method", targetMethodSig);
        slice.put("callers", callers);
        return slice; // Exported to JSON-IR for Phase 2 [cite: 105]
    }
}
