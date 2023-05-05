from core.utils import BaseLkView

from .services import malfunctions_get, malfunction_complete


class IndexView(BaseLkView):
    template_name = 'repairer/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['rows'] = malfunctions_get(request)

        return context


class MalfunctionComplete(BaseLkView):

    def get(self, request):
        return malfunction_complete(request)
