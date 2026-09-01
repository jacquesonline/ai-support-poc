const workbenchAnchors = new Set(["#control-room", "#harvey", "#improvement", "#proof-5"]);
if (workbenchAnchors.has(window.location.hash)) {
  window.location.replace(`/workbench/full${window.location.hash}`);
}
